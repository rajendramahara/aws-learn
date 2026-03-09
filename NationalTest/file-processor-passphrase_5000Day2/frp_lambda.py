import os
import json
import boto3
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

dict_table = dynamodb.Table(os.environ["DICTIONARY_TABLE"])
checks_table = dynamodb.Table(os.environ["CHECKS_TABLE"])
matches_table = dynamodb.Table(os.environ["MATCHES_TABLE"])

def atbash(s):
    res = []
    for ch in s:
        if 'a' <= ch <= 'z':
            res.append(chr(ord('z') - (ord(ch) - ord('a'))))
        else:
            res.append(ch)
    return ''.join(res)

def process_s3_file(bucket, key):
    print(f"Processing bucket={bucket}, key={key}")
    obj = s3.get_object(Bucket=bucket, Key=key)
    text = obj['Body'].read().decode().strip()
    
    # Extract middle 10 chars, reverse, lowercase, apply Atbash
    sub = text[2:-2]
    transformed = atbash(sub[::-1].lower())

    file_index = key.split('-')[1].split('.')[0]
    timestamp = datetime.utcnow().isoformat()

    result = dict_table.get_item(Key={'passphrase': transformed})
    if 'Item' in result:
        matches_table.put_item(Item={
            'file_index': file_index,
            'timestamp': timestamp,
            'passphrase': transformed,
            's3_key': key
        })
        print(f"[MATCH] Found match for {transformed} in file {key}")
    else:
        checks_table.put_item(Item={
            'file_index': file_index,
            'timestamp': timestamp,
            'passphrase_checked': transformed,
            'status': 'no_match',
            's3_key': key
        })
        print(f"[CHECK] No match for {transformed} in file {key}")

def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))

    for record in event['Records']:
        # ✅ Check if the event is from SNS or SQS
        if 'Sns' in record:
            sns_msg = json.loads(record['Sns']['Message'])
            print("✅✅✅✅✅SNS message:", sns_msg)
        elif 'body' in record:  # SQS event carrying SNS
            body = json.loads(record['body'])
            sns_msg = json.loads(body['Message'])
            print("✅✅✅✅✅SQS message:", sns_msg)
        else:
            print("⚠️ Unknown event format:", record)
            continue

        for rec in sns_msg['Records']:
            bucket = rec['s3']['bucket']['name']
            key = unquote_plus(rec['s3']['object']['key'])
            print(f"Processing bucket={bucket}, key={key}")
            process_s3_file(bucket, key)

    return {"status": "done"}                                                                                                                                                                                                                                                          
