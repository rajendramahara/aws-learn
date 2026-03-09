# with try-except blocks for error handling and logging
 
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

        # ----------------------------------------------------
        # STEP 1 — Decode SQS message
        # ----------------------------------------------------
        try:
            body = json.loads(record["body"])
        except:
            continue

        if "Message" not in body:
            continue

        try:
            sns_message = json.loads(body["Message"])
            print("SNS inner message:", sns_message)
        except:
            continue

        if "Records" not in sns_message:
            continue

        s3_info = sns_message["Records"][0]["s3"]
        bucket = s3_info["bucket"]["name"]
        key = urllib.parse.unquote_plus(s3_info["object"]["key"])

        print(f"S3 Bucket: {bucket}")
        print(f"S3 Key: {key}")

        image_id = key.split("/")[-1]

        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            image_bytes = obj["Body"].read()
        except Exception as e:
            continue

        # Rekognition Moderation
        try:
            rekog_result = rekognition.detect_moderation_labels(Image={"Bytes": image_bytes})
            labels = [lbl["Name"].lower() for lbl in rekog_result["ModerationLabels"]]
        except Exception as e:
            continue

        print("Detected labels:", labels)

        rules_data = RULES_TABLE.scan()
        sensitive_rules = [item["sensitive_label"].lower() for item in rules_data.get("Items", [])]

        print("Loaded sensitive rules:", sensitive_rules)

        matched = list(set(labels).intersection(set(sensitive_rules)))
        print("Matched sensitive labels:", matched)

        timestamp = datetime.utcnow().isoformat()

        try:
            CHECKS_TABLE.put_item(
                Item={
                    "image_id": image_id,
                    "timestamp": timestamp,
                    "detected_labels": labels,
                    "decision": "alert" if matched else "clean"
                }
            )
            print("✔ Inserted into ModerationChecks")
        except Exception as e:

        if matched:
            try:
                ALERTS_TABLE.put_item(
                    Item={
                        "image_id": image_id,
                        "timestamp": timestamp,
                        "sensitive_label": matched[0]
                    }
                )
                print("✔ Inserted into ModerationAlerts")
            except Exception as e:
                print("❌ Failed writing ModerationAlerts:", e)

            try:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="⚠ Sensitive Image Detected",
                    Message=f"Image '{image_id}' contains prohibited content: {matched[0]}"
                )
            except Exception as e:
                print("❌ SNS publish failed:", e)
        else:
            print("✔ Image is clean — no alert generated")

    return {"status": "done"}
