import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore.exceptions
import traceback
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
other_client=boto3.client("dynamodb")

def get_table():
    table = dynamodb.Table('CustomersAddresses')
    return table

def create_address(item):
    table = dynamodb.Table("CustomersAddresses")
    item['address_id'] = item['deliver_point_barcode']
    pk=item['address_id']

    response= None
    logger.info("Address lookup response3 = " + json.dumps(item,indent=2))
    try:
        logger.info("begin add")
        
        response = table.put_item(
            Item=item,
            #ConditionExpression='attribute_not_exists(address_id)'
        )
        logger.info("add item successfully")
        response=pk
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedEXception':
            print('Conditional expression failed')
            response=pk
        else:
            raise 
    except Exception as e:
        print("Exception = ",e)
        traceback.print_exc()
        raise e

    logging.info("Create response = " + str(response))
    return response

def get_address(address_id):
    table = dynamodb.Table("CustomersAddresses")

    response = table.get_item(
        Key=address_id
    )

    response = response.get('Item', None)
    return response