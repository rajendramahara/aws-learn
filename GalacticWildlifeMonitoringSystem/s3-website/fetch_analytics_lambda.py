# fetch_analytics
import json
import os
import boto3
from collections import defaultdict

dynamodb = boto3.client('dynamodb')
TABLE = os.environ.get('DDB_TABLE', 'WildlifeSightings')

def lambda_handler(event, context):
    # Scan table (note: not for production at scale)
    try:
        resp = dynamodb.scan(TableName=TABLE)
        items = resp.get('Items', [])
        total_submissions = len(items)
        per_species = defaultdict(int)
        latest = []
        # Build latest list (by timestamp) then slice
        for it in items:
            ts = it.get('timestamp', {}).get('S')
            ranger = it.get('ranger', {}).get('S')
            planet = it.get('planet', {}).get('S')
            sightings_json = it.get('sightings', {}).get('S','{}')
            try:
                sightings = json.loads(sightings_json)
            except:
                sightings = {}
            for k,v in sightings.items():
                try:
                    per_species[k] += int(v)
                except:
                    pass
            latest.append({"timestamp": ts, "ranger": ranger, "planet": planet, "sightings": sightings})
        latest_sorted = sorted(latest, key=lambda x: x.get('timestamp') or '', reverse=True)[:10]
        return {
            "statusCode": 200,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps({"total_submissions": total_submissions, "per_species": per_species, "latest": latest_sorted})
        }
    except Exception as e:
        return {"statusCode":500,"body":json.dumps({"error":str(e)})}
