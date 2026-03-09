import json
import hashlib
import os

# Store hashed password in env variable for better practice
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def lambda_handler(event, context):

    body = json.loads(event["body"])
    username = body.get("username")
    password = body.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

        token_raw = username + password
        token = hashlib.sha256(token_raw.encode()).hexdigest()

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Login successful",
                "token": token
            })
        }

    return {
        "statusCode": 401,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Invalid credentials"
        })
    }