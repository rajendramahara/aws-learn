import json
import boto3
import base64

# IMPORTANT: region must match this Lambda region
kms = boto3.client('kms', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb')

TABLE = "EncryptedMessages"

def lambda_handler(event, context):

    print("EVENT:", event)

    # Get query parameter safely
    params = event.get("queryStringParameters") or {}
    message_id = params.get("id")

    if not message_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "id query parameter required"})
        }

    table = dynamodb.Table(TABLE)

    response = table.get_item(Key={"id": message_id})

    if "Item" not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Message not found"})
        }

    encrypted_message = response["Item"]["encrypted_message"]

    decrypted = kms.decrypt(
        CiphertextBlob=base64.b64decode(encrypted_message)
    )

    plaintext = decrypted["Plaintext"].decode()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "decrypted_message": plaintext
        })
    }