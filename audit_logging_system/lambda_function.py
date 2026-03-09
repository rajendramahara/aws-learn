# DynamoDBAuditProcessor

import json
import os
import uuid
from datetime import datetime
import boto3

# Initialize the DynamoDB client and specify the destination table
DYNAMODB = boto3.resource('dynamodb')
AUDIT_TABLE_NAME = os.environ.get('AUDIT_TABLE_NAME', 'MyAppAuditLogTable')
AUDIT_TABLE = DYNAMODB.Table(AUDIT_TABLE_NAME)

def lambda_handler(event, context):
    
    # 1. Loop through all incoming stream records
    for record in event['Records']:
        
        # 2. Extract key event attributes
        event_name = record['eventName']
        table_name = record['eventSourceARN'].split('/')[1]
        timestamp = record['dynamodb']['ApproximateCreationDateTime']
        
        # DynamoDB Streams use a special data structure (DynamoDB JSON format)
        # We use a helper function (not shown, or manually) to unmarshall it to standard JSON/Python dict
        
        # Get the primary key for the item that changed
        # This corresponds to the 'P001' field in your audit log
        primary_key = record['dynamodb']['Keys']['ID']['S']
        
        # Get the new and old images
        new_image = record['dynamodb'].get('NewImage')
        old_image = record['dynamodb'].get('OldImage')
        
        # 3. Create the structured audit log entry
        audit_item = {
            'EventID': str(uuid.uuid4()),  # Generates the unique ID (e.g., cd6327b2-...)
            'Timestamp': datetime.utcfromtimestamp(timestamp).isoformat(),
            'TableName': table_name,
            'ItemKey': primary_key,
            'EventName': event_name,
            'NewData': json.dumps(new_image) if new_image else 'N/A',
            'OldData': json.dumps(old_image) if old_image else 'N/A',
            'Source': 'StreamTriggered',
        }
        
        # 4. Write the audit log entry to the destination table
        try:
            AUDIT_TABLE.put_item(Item=audit_item)
            print(f"Successfully logged {event_name} for key {primary_key}")
            
        except Exception as e:
            print(f"Error writing to audit table: {e}")
            # In a real app, you would log this error and potentially send it to a DLQ
            
    return {'statusCode': 200, 'body': f"Processed {len(event['Records'])} records."}