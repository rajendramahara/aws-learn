# process_sighting (Python 3.11)
import json
import os
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.client('dynamodb')
TABLE = os.environ.get('DDB_TABLE', 'WildlifeSightings')

# The required species list
SPECIES = [
  "Stellar Lynx","Nebula Eagle","Crimson Hornbeast","Void Panther",
  "Aqua Serpent","Moonlight Wolf","Quasar Turtle","Luminous Beetle",
  "Stormback Ape","Crystal Mantis"
]

def lambda_handler(event, context):
    # Expecting HTTP API format (event['body'] string)
    try:
        body = event.get('body')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body or {}
    except Exception as e:
        return respond(400, {"result":"invalid","error":"Malformed JSON: "+str(e)})
    
    # Basic validation
    missing = []
    if not data.get('ranger'):
        missing.append('ranger')
    if not data.get('planet'):
        missing.append('planet')
    if not isinstance(data.get('sightings'), dict):
        missing.append('sightings (must be object)')
    else:
        # Check species keys present and quantities >=0 integers
        for s in SPECIES:
            if s not in data['sightings']:
                missing.append(f"species missing: {s}")
            else:
                q = data['sightings'].get(s)
                # numeric check
                try:
                    qi = int(q)
                    if qi < 0:
                        missing.append(f"quantity negative for {s}")
                except Exception:
                    missing.append(f"quantity invalid for {s}")
    
    if missing:
        return respond(400, {"result":"invalid","error":"; ".join(missing)})
    
    # Create tracking token (simple)
    tracking_token = "GALAXY-TRK-" + uuid.uuid4().hex[:10].upper()
    item_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Prepare DynamoDB item (attribute values)
    # We'll store sightings as a JSON string to keep it simple
    try:
        dynamodb.put_item(
            TableName=TABLE,
            Item={
                "id": {"S": item_id},
                "timestamp": {"S": timestamp},
                "ranger": {"S": str(data['ranger'])},
                "planet": {"S": str(data['planet'])},
                "sightings": {"S": json.dumps(data['sightings'])},
                "tracking_token": {"S": tracking_token}
            }
        )
    except Exception as e:
        return respond(500, {"result":"invalid","error":"DynamoDB error: "+str(e)})
    
    return respond(200, {"result":"valid","tracking_token":tracking_token})

def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type":"application/json", "Access-Control-Allow-Origin":"*"},
        "body": json.dumps(body)
    }
