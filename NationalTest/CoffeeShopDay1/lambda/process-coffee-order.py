import json
import boto3
from datetime import datetime
from decimal import Decimal

# AWS resources
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# DynamoDB Tables
ORDERS = dynamodb.Table('CoffeeOrders')
DIY = dynamodb.Table('DIY')
STOCKS = dynamodb.Table('CoffeeStocks')

# S3 Bucket
BUCKET = "coffee-shop-app-day1"

INGREDIENT_COST = {
    "WR": Decimal("0.10"),
    "IC": Decimal("0.32"),
    "MK": Decimal("0.50"),
    "FM": Decimal("0.35"),
    "SR": Decimal("0.75"),
    "ES": Decimal("2.25"),
    "CP": Decimal("1.78"),
    "VI": Decimal("3.65"),
    "WY": Decimal("4.22")
}

RECIPES = {
 "Espresso":[("ES",1)],
 "Americano":[("ES",1),("WR",1)],
 "Flat White":[("ES",1),("MK",2)],
 "Doppio":[("ES",2)],
 "Macchiato":[("ES",1),("MK",1),("FM",1)],
 "Cappuccino":[("ES",1),("MK",1),("FM",2),("CP",1)],
 "Mocha":[("ES",1),("MK",1),("FM",2),("CP",2)],
 "Affogato":[("ES",2),("VI",1)],
 "Irish Coffee":[("ES",1),("WY",1),("SR",1),("FM",1)],
 "Iced Coffee":[("ES",1),("IC",2),("MK",2),("SR",2)]
}

PACKAGING = Decimal("2.25")

def lambda_handler(event, context):
    print("EVENT:", event)

    # ✅ Safe body parsing
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)

    item = body.get("order")
    if not item:
        return {"statusCode": 400, "body": "Missing order"}

    now = datetime.now()
    orderid = "Order-" + now.strftime("%Y-%m-%d-%H%M%S")

    ingredients = []

    # ✅ CUSTOM ORDER HANDLING (SAFE)
    if item == "Custom":
        for ing in body.get("ingredients", []):
            code = ing.get("itemcode") or ing.get("item")
            qty = ing.get("quantity", 0)

            if code and qty > 0:
                ingredients.append({
                    "itemcode": code,
                    "quantity": qty
                })

    # ✅ STANDARD ORDER (UNCHANGED)
    else:
        ingredients = [
            {"itemcode": k, "quantity": v}
            for k, v in RECIPES[item]
        ]

    # ✅ COST CALCULATION
    cost = sum(
        INGREDIENT_COST[i["itemcode"]] * Decimal(str(i["quantity"]))
        for i in ingredients
    ) + PACKAGING

    cost = cost.quantize(Decimal("0.01"))

    # ✅ SAVE ORDER
    ORDERS.put_item(Item={
        "orderid": orderid,
        "timestamp": now.isoformat(),
        "item": item,
        "cost": cost
    })

    # ✅ SAVE CUSTOM INGREDIENTS
    if item == "Custom":
        DIY.put_item(Item={
            "orderid": orderid,
            "ingredients": ingredients
        })

    # ✅ UPDATE STOCK
    for i in ingredients:
        STOCKS.update_item(
            Key={"item": i["itemcode"]},
            UpdateExpression="ADD consumedqty :q",
            ExpressionAttributeValues={
                ":q": Decimal(str(i["quantity"]))
            }
        )

    # ✅ SAVE TO S3
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{orderid}.txt",
        Body=f"{item}, {cost}"
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "response": "accepted",
            "item": item,
            "cost": float(cost)
        })
    }
