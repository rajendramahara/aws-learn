import json
import uuid
import boto3
from datetime import datetime, timedelta
import random
import os

dynamodb = boto3.client("dynamodb")
TABLE = os.environ.get("DDB_TABLE", "InterstellarDeliveries")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        return respond(400, {"error": "Invalid JSON"})

    required = ["sender", "sender_planet", "receiver", "receiver_planet", "weight", "priority"]
    missing = [f for f in required if f not in body or not body[f]]
    if missing:
        return respond(400, {"error": "Missing fields: " + ", ".join(missing)})

    try:
        weight = float(body["weight"])
        if weight <= 0:
            return respond(400, {"error": "Weight must be > 0"})
    except:
        return respond(400, {"error": "Invalid weight"})

    tracking_id = "TRK-" + uuid.uuid4().hex[:10].upper()
    created_at = datetime.utcnow().isoformat() + "Z"

    eta_hours = random.randint(12, 96)
    eta = (datetime.utcnow() + timedelta(hours=eta_hours)).isoformat() + "Z"

    try:
        dynamodb.put_item(
            TableName=TABLE,
            Item={
                "id": {"S": tracking_id},
                "created_at": {"S": created_at},
                "sender": {"S": body["sender"]},
                "sender_planet": {"S": body["sender_planet"]},
                "receiver": {"S": body["receiver"]},
                "receiver_planet": {"S": body["receiver_planet"]},
                "weight": {"N": str(weight)},
                "priority": {"S": body["priority"]},
                "status": {"S": "Preparing for dispatch"},
                "eta": {"S": eta}
            }
        )
    except Exception as e:
        return respond(500, {"error": "DynamoDB error: " + str(e)})

    return respond(200, {"tracking_id": tracking_id, "eta": eta})

def respond(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }
