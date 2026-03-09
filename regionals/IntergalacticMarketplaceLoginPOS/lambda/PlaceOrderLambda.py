import json
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("IntergalacticOrdersNew")

def lambda_handler(event, context):

    body = json.loads(event.get("body", "{}"))

    agent = body.get("agent")
    items = body.get("items")

    # Validate input
    if not agent or not items or len(items) == 0:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Invalid input"})
        }

    # Generate metadata
    order_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S")

    order_data = {
        "agent": agent,
        "items": items
    }

    # Simple signature
    signature = f"{order_id}-{timestamp}"

    # Store in DynamoDB
    table.put_item(
        Item={
            "orderId": order_id,        # Make sure this matches your table partition key
            "Timestamp": timestamp,
            "OrderData": order_data,
            "OrderSignature": signature
        }
    )

    # Success response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps({
            "result": "success",
            "orderId": order_id,
            "timestamp": timestamp,
            "signature": signature
        })
    }