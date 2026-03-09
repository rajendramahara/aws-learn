import json
import boto3
import uuid
import urllib.parse
from decimal import Decimal

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
OUTPUT_BUCKET = 'img-rekognition-output'
TABLE_NAME = 'ImageMetadata'
table = dynamodb.Table(TABLE_NAME)

CATEGORY_KEYWORDS = {
    'Dog': ['Dog', 'Pet', 'Mammal'],
    'Cat': ['Cat', 'Pet', 'Mammal'],
    'Humans': ['Person', 'Human'],
    'Vehicles': ['Car', 'Truck', 'Bus', 'Vehicle', 'Motorcycle'],
    'Grass': ['Grass', 'Plant', 'Tree', 'Field', 'Nature'],
    'Unsafe': ['Weapon', 'Gun', 'Knife', 'Alcohol']
}

CONFIDENCE_THRESHOLD = 80

def lambda_handler(event, context):
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = record['object']['key']
    
    # Call Rekognition
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=20
    )
    
    labels = response['Labels']
    
    print("Rekognition labels:", labels)
    
    best_category = 'unknown'
    best_confidence = 0
    
    for label in labels:
        label_name = label['Name']
        label_conf = label['Confidence']
        
        if label_conf < CONFIDENCE_THRESHOLD:
            continue  # ignore low-confidence labels
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            if label_name in keywords and label_conf > best_confidence:
                best_category = category
                best_confidence = label_conf
                
    print(f"Selected category: {best_category} (Confidence: {best_confidence})")
    
    # Save metadata in DynamoDB
    table.put_item(
        Item={
            'image_id': str(uuid.uuid4()),
            'image_key': key,
            'category': best_category,
            'labels': [l['Name'] for l in labels],
            'confidence': [Decimal(str(l['Confidence'])) for l in labels]
        }
    )
    
    # Copy image to output bucket (auto-create folder)
    s3.copy_object(
        Bucket=OUTPUT_BUCKET,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=f"{best_category}/{key.split('/')[-1]}"
    )
    
    return {
        'status': 'success',
        'category': best_category
    }
