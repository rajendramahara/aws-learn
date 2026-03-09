import json
import boto3
import uuid
from datetime import datetime

s3 = boto3.client("s3")
BUCKER_NAME = "secure-doc-bucket-gj"

def lambda_handler(event, context):
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event

    file_name = body["filename"]
    user_id = body["userId"]

    document_id = str(uuid.uuid4())

    s3.put_object(
        Bucket=BUCKER_NAME,
        Key=f"raw/{document_id}_{file_name}",
        Body=b"Dummy file content",
        ServerSideEncryption="aws:kms"
    )

    return {
        statusCode": 200,
        "body": json.dumps({
            "message": "File uploaded successfully",
            "documentId": document_id
        })
    }