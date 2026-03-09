import json 
import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

ORDERS = dynamodb.Table('CoffeeOrders')
DIY = dynamodb.Table('DIY')
STOCKS = dynamodb.Table('CoffeeStocks')

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
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)
    item = body.get("order")
    if not item:
        return {"statusCode": 400, "body": "Missing order"}

    nowDate = datetime.now()
    orderid = "Order-" + nowDate.strftime("%Y-%m-%d-%H%M%S")
    ingredients = []

    if item == "Custom":
        for ing in body.get("ingredients", []):
            code = ing.get("itemcode")
            qty = ing.get("quantity", 0)
            if code and qty > 0:
                ingredients.append({"itemcode": code, "quantity": qty})
    else:
        ingredients = [
            {"itemcode": k, "quantity": v}
            for k, v in RECIPES[item]
        ]
    cost = sum(INGREDIENT_COST)