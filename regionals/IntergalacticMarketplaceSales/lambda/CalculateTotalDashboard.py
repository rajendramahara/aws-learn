import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrdersNew')

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

    response = table.scan()
    orders = response.get("Items", [])

    item_totals = {}
    grand_total = 0

    for order in orders:
        items = order["OrderData"]["items"]

        for item, qty in items.items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)
            grand_total += int(qty)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "total_orders": len(orders),
            "item_totals": convert_decimal(item_totals),
            "grand_total": grand_total
        })
    }