import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
ORDERS = dynamodb.Table('CoffeeOrders')

def lambda_handler(event, context):

    response = ORDERS.scan()
    items = response['Items']

    # Convert Decimal to float
    for item in items:
        item['cost'] = float(item['cost'])

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(items)
    }

# import json
# import boto3
# from decimal import Decimal

# dynamodb = boto3.resource("dynamodb")
# ORDERS = dynamodb.Table("CoffeeOrders")

# def decimal_to_float(obj):
#     if isinstance(obj, Decimal):
#         return float(obj)
#     return obj

# def lambda_handler(event, context):
#     response = ORDERS.scan()
#     items = response.get("Items", [])

#     return {
#         "statusCode": 200,
#         "headers": {
#             "Access-Control-Allow-Origin": "*"
#         },
#         "body": json.dumps({
#             "orders": items
#         }, default=decimal_to_float)
#     }