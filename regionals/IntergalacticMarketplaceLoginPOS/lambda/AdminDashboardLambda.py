import boto3
import json
import hashlib
from decimal import Decimal

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrdersNew')

# Admin credentials (must match Login Lambda)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Generate valid token (same logic as Login Lambda)
VALID_TOKEN = hashlib.sha256(
    (ADMIN_USERNAME + ADMIN_PASSWORD).encode()
).hexdigest()


# -------- Helper: Convert Decimal to int --------
def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj)
    else:
        return obj


def lambda_handler(event, context):

    # -------- Token Validation --------
    headers = event.get("headers", {})
    token = headers.get("Authorization") or headers.get("authorization")

    if token != VALID_TOKEN:
        return {
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"message": "Unauthorized"})
        }

    # -------- Fetch Orders --------
    response = table.scan()
    orders = response.get("Items", [])

    total_orders = len(orders)
    item_totals = {}

    for order in orders:

        order_data = order.get("OrderData", {})
        items = order_data.get("items", {})

        for item, qty in items.items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)

    most_ordered = None
    if item_totals:
        most_ordered = max(item_totals, key=item_totals.get)

    # -------- Convert Decimal --------
    orders = convert_decimal(orders)
    item_totals = convert_decimal(item_totals)

    # -------- Return Success --------
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "total_orders": total_orders,
            "item_totals": item_totals,
            "most_ordered_item": most_ordered,
            "orders": orders
        })
    }