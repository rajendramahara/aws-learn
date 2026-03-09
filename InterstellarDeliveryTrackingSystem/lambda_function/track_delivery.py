import json
import boto3
import os

dynamodb = boto3.client("dynamodb")
TABLE = os.environ.get("DDB_TABLE", "InterstellarDeliveries")

def lambda_handler(event, context):

    print("DEBUG event:", event)

    # ----------------------------
    # 1) If no ticket param → return list of all tracking IDs
    # ----------------------------
    params = event.get("queryStringParameters") or {}
    ticket = params.get("ticket")

    if not ticket:
        # Return all IDs
        resp = dynamodb.scan(
            TableName=TABLE,
            ProjectionExpression="id"
        )

        ids = [item["id"]["S"] for item in resp.get("Items", [])]

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "mode": "all_ids",
                "tracking_ids": ids
            })
        }

    # ----------------------------
    # 2) If ticket param present → return that record
    # ----------------------------
    resp = dynamodb.get_item(
        TableName=TABLE,
        Key={"id": {"S": ticket}}
    )

    if "Item" not in resp:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Tracking ID not found"})
        }

    it = resp["Item"]

    result = {
        "tracking_id": ticket,
        "status": it["status"]["S"],
        "sender": it["sender"]["S"],
        "receiver": it["receiver"]["S"],
        "sender_planet": it["sender_planet"]["S"],
        "receiver_planet": it["receiver_planet"]["S"],
        "priority": it["priority"]["S"],
        "eta": it["eta"]["S"],
        "weight": it["weight"]["N"],
        "created_at": it["created_at"]["S"]
    }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result)
    }
