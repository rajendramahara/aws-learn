import json
import json
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("IntergalacticMarketplace")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        agent = body.get("agent")
        items = body.get("items")

        if not agent or not items:
            return {
                "statusCode": 400,
                "body": json.dumps({"result": "Invalid data"})
            }

        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # signature = order_id + timestamp (VERY SIMPLE for now)
        signature = f"{order_id}-{timestamp}"

        table.put_item(
            Item={
                "order_id": order_id,
                "timestamp": timestamp,
                "agent": agent,
                "items": json.dumps(items),
                "signature": signature
            }
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "result": "success",
                "order_id": order_id,
                "timestamp": timestamp,
                "signature": signature
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
