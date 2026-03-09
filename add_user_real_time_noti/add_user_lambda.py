import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        if not body.get("username") or not body.get("email"):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({'message': 'Username and email are required'})
            }
        user_id = str(uuid.uuid4())

        # Prepare DynamoDB item
        params = {
            "TableName": "Users",
            "Item": {
                "id": {"S": user_id},
                "username": {"S": body["username"]},
                "email": {"S": body["email"]},
                "created_at": {"S": datetime.utcnow().isoformat()}
            }
        }

        # Insert into DynamoDB
        dynamodb.put_item(**params)

        # Send SNS notification
        sns_message = f"New user added:\nUsername: {body['username']}\nEmail: {body['email']}"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=sns_message,
            Subject="New User Added"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "message": "User saved successfully!",
                "user": {"id": user_id, "username": body["username"], "email": body["email"]}
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "message": "Error saving user",
                "error": str(e)
            })
        }