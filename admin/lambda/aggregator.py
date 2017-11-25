from __future__ import print_function
import boto3
import json
import decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeDeserializer

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('FulfilledOrdersReqsAgg')
des = TypeDeserializer()


def lambda_handler(event, context):
    for record in event['Records']:
        d = {}
        print(record['eventID'])
        print(record['eventName']) 
        #print(record['dynamodb'])
        
        if record['eventName'] == 'INSERT':
            try:
                for key in record['dynamodb']['NewImage']:
                    d[key] = des.deserialize(record['dynamodb']['NewImage'][key])
                apiKey = d['APIKey']
            
                response = table.update_item(
                    Key={
                        'APIKey': apiKey
                    },
                    UpdateExpression="SET resources = if_not_exists(resources, :start) + :val",
                    ExpressionAttributeValues={
                        ':val': decimal.Decimal(1),
                        ':start': 0,
                    },
                    ReturnValues="UPDATED_NEW"
                )
            
                print("UpdateItem succeeded:")
                print(json.dumps(response, indent=4, cls=DecimalEncoder))
            except ClientError as e:
                print("SOMETHING WENT WRONG")
                print(e)
        
    print('Successfully processed %s records.' % str(len(event['Records'])))