import json
import boto3
import csv
import uuid
import urllib.parse

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrdersNew')

AGENT_NAME = "STAR-AGENT-07"   # 🔥 change to your real agent name

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    reader = csv.DictReader(content.splitlines())

    for row in reader:

        original_timestamp = row["Timestamp"]

        # Parse CSV OrderData JSON string
        parsed_items = json.loads(row["OrderData"])

        if sum(parsed_items.values()) == 0:
            continue

        # ✅ Wrap inside required structure
        order_data = {
            "items": parsed_items,
            "agent": AGENT_NAME
        }

        order_id = str(uuid.uuid4())

        # ✅ Signature format exactly like you showed
        order_signature = f"{order_id}-{original_timestamp}"

        table.put_item(
            Item={
                "orderId": order_id,
                "OrderData": order_data,
                "OrderSignature": order_signature,
                "Timestamp": original_timestamp
            }
        )

    return {
        "statusCode": 200,
        "body": "CSV Orders Processed Successfully"
    }