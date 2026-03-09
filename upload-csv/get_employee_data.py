import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Employees')

def lambda_handler(event, context):
    # TODO implement
    response = table.scan()
    data = response['Items']

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        'body': json.dumps(data)
    }
