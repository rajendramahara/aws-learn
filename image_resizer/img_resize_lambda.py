from urllib.parse import unquote_plus
import boto3
from PIL import Image
import io
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    # Read from environment variables
    dest_bucket = os.environ['DEST_BUCKET']
    sizes_str = os.environ.get('THUMBNAIL_SIZES', "64x64,128x128,256x256")
    sizes = [tuple(map(int, size.split('x'))) for size in sizes_str.split(",")]
    
    obj = s3.get_object(Bucket=source_bucket, Key=key)
    img = Image.open(obj['Body'])

    for size in sizes:
        thumbnail = img.copy()
        thumbnail.thumbnail(size)

        if thumbnail.mode in ("RGBA", "P"):
            thumbnail = thumbnail.convert("RGB")

        buffer = io.BytesIO()
        thumbnail.save(buffer, "JPEG")
        buffer.seek(0)

        new_key = f"thumbnails/{size[0]}x{size[1]}-{key.split('/')[-1].split('.')[0]}.jpg"
        s3.put_object(Bucket=dest_bucket, Key=new_key, Body=buffer, ContentType="image/jpeg")

    return {"statusCode": 200, "body": f"Thumbnails created for {key}"}

