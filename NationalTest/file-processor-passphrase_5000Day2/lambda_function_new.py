import json
import boto3
import string
from datetime import datetime

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Tables
dictionary_table = dynamodb.Table("Dictionary")
checks_table = dynamodb.Table("Checks")
matches_table = dynamodb.Table("Matches")


# -------------------------------
# Atbash Cipher Function
# -------------------------------
def atbash_cipher(text: str) -> str:
    """
    Convert text using Atbash substitution cipher.
    Only alphabets are transformed.
    Numbers remain unchanged.
    """

    alphabet = string.ascii_lowercase
    reversed_alphabet = alphabet[::-1]

    translation_table = str.maketrans(
        alphabet,
        reversed_alphabet
    )

    return text.translate(translation_table)


# -------------------------------
# Passphrase Decode Logic
# -------------------------------
def decode_passphrase(raw_text: str) -> str:
    """
    Implements Module 3 logic exactly:

    1. Ensure 14 chars
    2. Remove first 2 + last 2
    3. Reverse
    4. Lowercase
    5. Apply Atbash
    """

    # Validation
    if len(raw_text) != 14:
        raise ValueError(
            f"Invalid string length: {len(raw_text)}"
        )

    # Step 1 — Trim
    trimmed = raw_text[2:-2]
    # Step 2 — Reverse
    reversed_text = trimmed[::-1]
    # Step 3 — Lowercase
    lowered_text = reversed_text.lower()
    # Step 4 — Atbash
    decoded = atbash_cipher(lowered_text)

    return decoded


def log_match(file_index, passphrase):

    timestamp = datetime.utcnow().isoformat()

    matches_table.put_item(
        Item={
            "timestamp": timestamp,
            "file_index": int(file_index),
            "passphrase": passphrase
        }
    )


def log_check(file_index, passphrase):

    timestamp = datetime.utcnow().isoformat()

    checks_table.put_item(
        Item={
            "timestamp": timestamp,
            "file_index": int(file_index),
            "passphrase": passphrase
        }
    )


def lambda_handler(event, context):

    for record in event["Records"]:

        # SNS → SQS → Lambda structure
        body = json.loads(record["body"])
        message = json.loads(body["Message"])

        s3_info = message["Records"][0]["s3"]

        bucket = s3_info["bucket"]["name"]
        key = s3_info["object"]["key"]

        # Extract file index
        # frp-5678.txt → 5678
        file_index = key.split("-")[1].split(".")[0]

        try:
            # Read file from S3
            obj = s3.get_object(
                Bucket=bucket,
                Key=key
            )

            raw_text = obj["Body"].read().decode().strip()

            # Decode passphrase
            decoded_passphrase = decode_passphrase(raw_text)

            # Check Dictionary
            response = dictionary_table.get_item(
                Key={
                    "passphrase": decoded_passphrase
                }
            )

            # If match found
            if "Item" in response:
                log_match(file_index, decoded_passphrase)

            else:
                log_check(file_index, decoded_passphrase)

        except Exception as e:

            print(f"Error processing {key}: {str(e)}")

    return {
        "statusCode": 200,
        "body": "Processing completed"
    }
