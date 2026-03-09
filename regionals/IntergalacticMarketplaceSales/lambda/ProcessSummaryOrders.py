import json
import boto3
import uuid
import urllib.request
import urllib.parse
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrdersNew')

DECRYPT_API_URL = "https://j2v45exrmd.execute-api.us-east-1.amazonaws.com/prod/decsummary"
HELPER_API_URL = "https://j2v45exrmd.execute-api.us-east-1.amazonaws.com/prod/validate"

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    # Read encrypted file
    response = s3.get_object(Bucket=bucket, Key=key)
    encrypted_content = response['Body'].read().decode('utf-8')

    # 🔹 STEP 1: Send RAW encrypted payload to Decrypt API
    decrypt_request = urllib.request.Request(
        DECRYPT_API_URL,
        data=encrypted_content.encode('utf-8'),
        method='POST'
    )

    decrypt_response = urllib.request.urlopen(decrypt_request)
    decrypted_result = json.loads(decrypt_response.read().decode())

    # Only continue if accepted
    if decrypted_result.get("response") != "accepted":
        return {"statusCode": 400, "body": "Decryption failed"}

    # 🔹 STEP 2: Format for Helper API
    order_data = {
        "agent": decrypted_result["agent"],
        "items": decrypted_result["sales"]
    }

    helper_body = json.dumps({
        "orderData": order_data
    }).encode('utf-8')

    helper_request = urllib.request.Request(
        HELPER_API_URL,
        data=helper_body,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    helper_response = urllib.request.urlopen(helper_request)
    helper_result = json.loads(helper_response.read().decode())

    if helper_result.get("response") != "accepted":
        return {"statusCode": 400, "body": "Validation failed"}

    # 🔹 STEP 3: Store in DynamoDB
    table.put_item(
        Item={
            "orderId": str(uuid.uuid4()),
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S"),
            "OrderData": order_data,
            "OrderSignature": helper_result["orderSignature"]
        }
    )

    return {
        "statusCode": 200,
        "body": "Summary Processed Successfully"
    }
