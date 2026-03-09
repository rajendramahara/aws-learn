import json
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource("dynamodb")
ses = boto3.client("ses")   # SES client
table = dynamodb.Table("IntergalacticMarketplace")

SENDER_EMAIL = "xajep19483@datehype.com"  #your-verified-email@example.com
RECEIVER_EMAIL = "xajep19483@datehype.com"   #receiver@example.com

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        agent = body.get("agent")
        items = body.get("items")

        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        signature = f"{order_id}-{timestamp}"

        # Save order
        table.put_item(
            Item={
                "order_id": order_id,
                "timestamp": timestamp,
                "agent": agent,
                "items": json.dumps(items),
                "signature": signature
            }
        )

        # ===== SEND EMAIL USING SES =====
        email_body = f"""
        New Order Received!\n\n
        Agent: {agent}\n
        Order ID: {order_id}\n
        Timestamp: {timestamp}\n
        Items: {json.dumps(items, indent=2)}\n
        """

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [RECEIVER_EMAIL]},
            Message={
                "Subject": {"Data": "New Intergalactic Order"},
                "Body": {"Text": {"Data": email_body}}
            }
        )

        # Return response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "result": "success",
                "order_id": order_id,
                "timestamp": timestamp,
                "signature": signature
            })
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
