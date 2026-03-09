import json
import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

DEST_BUCKET = "my-resized-images"

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    print("Source bucket:", source_bucket)
    print("File:", object_key)

    response = s3.get_object(Bucket=source_bucket, Key=object_key)
    image_content = response['Body'].read()

    # Open image using PIL
    image = Image.open(io.BytesIO(image_content))

    resized_image = image.resize((300, 300))

    # Save resized image to memory
    buffer = io.BytesIO()
    resized_image.save(buffer, format=image.format)
    buffer.seek(0)

    s3.put_object(
        Bucket=DEST_BUCKET,
        Key="resized-" + object_key,
        Body=buffer,
        ContentType=response['ContentType']
    )

    return {
        'statusCode': 200,
        'body': 'Image resized successfully!'
    }