import boto3
import json
import urllib.parse
from datetime import datetime

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

RULES_TABLE = dynamodb.Table("ModerationRules")
CHECKS_TABLE = dynamodb.Table("ModerationChecks")
ALERTS_TABLE = dynamodb.Table("ModerationAlerts")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:842273289878:ImageUploadTopic"


def lambda_handler(event, context):

    print("===== NEW INVOCATION =====")
    print(json.dumps(event, indent=4))

    for record in event["Records"]:

        # STEP 1 — Read SQS body
        body = json.loads(record["body"])

        # SQS → SNS → S3 event
        sns_message = json.loads(body["Message"])
        print("SNS inner message:", sns_message)

        # STEP 2 — Extract S3 info
        s3_info = sns_message["Records"][0]["s3"]
        bucket = s3_info["bucket"]["name"]
        key = urllib.parse.unquote_plus(s3_info["object"]["key"])

        print("Bucket:", bucket)
        print("Key:", key)

        image_id = key.split("/")[-1]

        # STEP 3 — Load image
        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj["Body"].read()

        # STEP 4 — Rekognition Moderation
        rekog = rekognition.detect_moderation_labels(
            Image={"Bytes": image_bytes}
        )

        labels = [lbl["Name"].lower() for lbl in rekog["ModerationLabels"]]
        print("Detected labels:", labels)

        # STEP 5 — Load sensitive rules (lowercase!)
        rules = RULES_TABLE.scan()["Items"]
        sensitive_rules = [r["sensitive_label"].lower() for r in rules]

        print("Sensitive rules:", sensitive_rules)

        # STEP 6 — Matching
        matched = list(set(labels).intersection(set(sensitive_rules)))
        print("Matched:", matched)

        timestamp = datetime.utcnow().isoformat()

        # STEP 7 — Always insert into ModerationChecks
        CHECKS_TABLE.put_item(
            Item={
                "image_id": image_id,
                "timestamp": timestamp,
                "detected_labels": labels,
                "decision": "alert" if matched else "clean"
            }
        )
        print("✔ Inserted into ModerationChecks")

        # STEP 8 — Insert into ModerationAlerts + SNS (ONLY if matched)
        if matched:

            ALERTS_TABLE.put_item(
                Item={
                    "image_id": image_id,
                    "timestamp": timestamp,
                    "sensitive_label": matched[0]
                }
            )
            print("✔ Inserted into ModerationAlerts")

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠ Sensitive Image Detected",
                Message=f"Image '{image_id}' contains prohibited content: {matched[0]}"
            )
            print("✔ SNS alert sent")

        else:
            print("✔ Image is clean — no alert generated")

    return {"status": "done"}
