import json
import boto3
import requests
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IntergalacticOrders')

# Decrypt API
DECRYPT_API = "https://sandbox.ethnustech.com/order/decsummary"

def lambda_handler(event, context):

    summary_files = [
        "y1.txt",
        "y2.txt",
        "y3.txt",
        "y4.txt",
        "y5.txt"
    ]

    grand_totals = {}

    for file_name in summary_files:

        # STEP 1 — Download encrypted file
        encrypted_text = download_summary(file_name)
        # STEP 2 — Decrypt
        decrypted_data = decrypt_summary(encrypted_text)
        # STEP 3 — Store in DB
        store_summary(decrypted_data, file_name)
        # STEP 4 — Aggregate totals
        for item, qty in decrypted_data["sales"].items():
            grand_totals[item] = grand_totals.get(item, 0) + qty

    return {
        "status": "Processed",
        "totals": grand_totals
    }

# Download encrypted summary
def download_summary(file_name):

    url = f"https://sandbox.ethnustech.com/order/summary/{file_name}"

    response = requests.get(url)

    return response.text

# Call decrypt API
def decrypt_summary(encrypted_text):

    response = requests.post(
        DECRYPT_API,
        data=encrypted_text,
        headers={"Content-Type": "text/plain"}
    )

    return response.json()

# Store in DynamoDB
def store_summary(data, file_name):

    table.put_item(
        Item={
            "OrderID": f"SUMMARY-{file_name}",
            "Timestamp": datetime.utcnow().isoformat(),
            "OrderData": data["sales"],
            "Agent": data["agent"],
            "OrderSignature": "SUMMARY-SIGNATURE"
        }
    )
