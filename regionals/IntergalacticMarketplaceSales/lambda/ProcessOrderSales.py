import json
import boto3
import csv
import uuid
import urllib.parse
import urllib.request

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrdersNew')

AGENT_NAME = "STAR-AGENT-Json"
HELPER_API_URL = "https://j2v45exrmd.execute-api.us-east-1.amazonaws.com/prod/validate"

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    reader = csv.DictReader(content.splitlines())

    for row in reader:

        original_timestamp = row["Timestamp"]
        parsed_items = json.loads(row["OrderData"])

        if sum(parsed_items.values()) == 0:
            continue

        # Required structure for helper API
        order_data = {
            "items": parsed_items,
            "agent": AGENT_NAME
        }

        # ✅ CALL HELPER API
        request_body = json.dumps({
            "orderData": order_data
        }).encode('utf-8')

        http_req = urllib.request.Request(
            HELPER_API_URL,
            data=request_body,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        api_response = urllib.request.urlopen(http_req)
        result = json.loads(api_response.read().decode())

        # ✅ Only store if accepted
        if result.get("response") == "accepted":

            order_id = str(uuid.uuid4())
            table.put_item(
                Item={
                    "orderId": order_id,
                    "OrderData": order_data,
                    "OrderSignature": result["orderSignature"],  # from API
                    "Timestamp": original_timestamp
                }
            )

    return {
        "statusCode": 200,
        "body": "CSV Orders Processed Successfully"
    }