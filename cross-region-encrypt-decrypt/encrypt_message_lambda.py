import json
import boto3
import base64
import uuid

kms = boto3.client('kms')
dynamodb = boto3.resource('dynamodb')

TABLE = "EncryptedMessages"
KEY_ID = "arn:aws:kms:us-east-1:800939197474:key/mrk-78dcb2d6153c401eb0f4bea3f5a1a556"

def lambda_handler(event, context):

    print("Full Event:", event)

    # Safely extract body
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event   # for lambda console test

    message = body.get("message")

    if not message:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Message is required"})
        }

    encrypted = kms.encrypt(
        KeyId=KEY_ID,
        Plaintext=message.encode()
    )

    cipher_text = base64.b64encode(
        encrypted['CiphertextBlob']
    ).decode()

    table = dynamodb.Table(TABLE)

    message_id = str(uuid.uuid4())

    table.put_item(
        Item={
            "id": message_id,
            "encrypted_message": cipher_text
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message_id": message_id
        })
    }