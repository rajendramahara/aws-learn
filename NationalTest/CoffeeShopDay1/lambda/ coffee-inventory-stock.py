import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
STOCKS = dynamodb.Table("CoffeeStocks")

def lambda_handler(event, context):
    
    response = STOCKS.scan()
    items = response['Items']

    stock_list = []

    for item in items:
        stock_list.append({
            "itemcode": item["item"],
            "quantity": float(item["consumedqty"])
        })

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "stock": stock_list
        })
    }

# def lambda_handler(event, context):
#     response = STOCKS.scan()
#     items = response.get("Items", [])

#     stock_list = [
#         {
#             "itemcode": i["item"],
#             "quantity": int(i.get("consumedqty", 0))
#         }
#         for i in items
#     ]

#     return {
#         "statusCode": 200,
#         "headers": {
#             "Access-Control-Allow-Origin": "*"
#         },
#         "body": json.dumps({
#             "stock": stock_list
#         })
#     }

