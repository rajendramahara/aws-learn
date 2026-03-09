import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
ORDERS = dynamodb.Table("CoffeeOrders")

def lambda_handler(event, context):
    response = ORDERS.scan()
    items = response.get("Items", [])

    total_orders = len(items)
    custom_orders = sum(1 for i in items if i.get("item") == "Custom")
    total_sales = sum(Decimal(str(i["cost"])) for i in items)
    average = total_sales / total_orders if total_orders else 0

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "orders": total_orders,
            "customizations": custom_orders,
            "average": float(round(average, 2)),
            "sum": float(round(total_sales, 2))
        })
    }
