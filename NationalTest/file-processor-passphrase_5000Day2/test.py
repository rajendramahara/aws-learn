import os
import json
import boto3
import string
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

dictionary_table = dynamodb.Table(os.environ["DICTIONARY_TABLE"])
checks_table = dynamodb.Table(os.environ["CHECKS_TABLE"])
matches_table = dynamodb.Table(os.environ["MATCHES_TABLE"])


def atbash(text):
    alphabet = string.ascii_lowercase
    reversed_alphabet = alphabet[::-1]
    table = str.maketrans(alphabet, reversed_alphabet)
    return text.translate(table)

def decode_passphrase(text):

    text = text.strip()
    if len(text) != 14:
        raise ValueError(f"Invalid length: {len(text)}")

    # Remove first 2 + last 2
    text = text[2:-2]
    # Reverse + lowercase
    text = text[::-1].lower()

    return atbash(text)

def lambda_handler(event, context):

    for record in event["Records"]:

        # SNS → SQS message
        body = json.loads(record["body"])
        message = json.loads(body["Message"])
        s3_info = message["Records"][0]["s3"]

        bucket = s3_info["bucket"]["name"]
        key = s3_info["object"]["key"]

        file_index = key.split("-")[1].split(".")[0]

        try:
            # Read file
            obj = s3.get_object(Bucket=bucket, Key=key)
            raw_text = obj["Body"].read().decode()

            # Decode passphrase
            passphrase = decode_passphrase(raw_text)

            # Check dictionary
            result = dictionary_table.get_item(
                Key={"passphrase": passphrase}
            )

            timestamp = datetime.utcnow().isoformat()

            if "Item" in result:
                matches_table.put_item(
                    Item={
                        "timestamp": timestamp,
                        "file_index": int(file_index),
                        "passphrase": passphrase
                    }
                )
                print(f"MATCH → {file_index}")

            else:
                checks_table.put_item(
                    Item={
                        "timestamp": timestamp,
                        "file_index": int(file_index),
                        "passphrase": passphrase
                    }
                )
                print(f"CHECK → {file_index}")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")

    return {"statusCode": 200}
