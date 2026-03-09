import json
import boto3
from collections import Counter

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("IntergalacticMarketplace")

def lambda_handler(event, context):
    response = table.scan()

    items_list = response.get("Items", [])

    total_orders = len(items_list)
    counter = Counter()

    for o in items_list:
        data = json.loads(o["items"])
        for k, v in data.items():
            counter[k] += int(v)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "total_orders": total_orders,
            "item_totals": dict(counter)
        })
    }
