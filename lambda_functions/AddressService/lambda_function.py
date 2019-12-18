import sys

sys.path.append('./')
sys.path.append('./requests')

import json
import boto3
from botocore.exceptions import ClientError
import logging
import botocore.vendored.requests as requests
from botocore.vendored.requests.auth import HTTPBasicAuth
import os
import addressdo
import app_context


os.environ['smarty_config'] = 'https://us-street.api.smartystreets.com/street-address'
os.environ['auth-id'] = 'c7348dd7-ff86-2223-48f0-ad21d3948ea1'
os.environ['auth-token'] = 'gzLyqDQoVRml7O0TOgAC'

address_url = os.environ['smarty_config']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

def validate_address(address,context):
    params = {}

    params['auth-id'] = context['auth-id']
    params['auth-token'] = context['auth-token']
    url = context['address_url']

    if (params['auth-id'] is None) or (params['auth-token'] is None) or (url is None):
        logger.error("Could get security info or environment")
        return 500
   
    try:
        params['street'] = address['street']

        state = address.get('state',None)
        if state is not None:
            params['state'] = state

        city = address.get('city',None)
        if city is not None:
            params['city']=city

        zipcode = address.get('zipcode',None)
        if zipcode is not None:
            params['zipcode']=zipcode
    except KeyError as ke:
        logger.info("Input was not valid")
        logger.info(str(ke))
        return 422

    result = requests.get(url, params=params)

    if result.status_code == 200:
        j_data = result.json()
        if j_data is None or j_data == []:
            logger.info("j_data is none ")
            rsp=None
        else:
            logger.info(json.dumps(j_data))
            if len(j_data) > 1:
                rsp = None
            else:
                rsp = j_data[0]['components']
                rsp['deliver_point_barcode'] = j_data[0]['delivery_point_barcode']
    else:
        rsp = None

    logger.info("Address lookup response = " + json.dumps(rsp,indent=2))
    return rsp

def get_context():

    context = {}

    context["address_url"] = os.environ['smarty_config']
    context["auth-id"] = os.environ['auth-id']
    context["auth-token"]=os.environ['auth-token']

    return context

def create_address(address):
    context = get_context()
    item=validate_address(address,context)
    logger.info("Address lookup response2 = " + json.dumps(item,indent=2))
    if item != None:
        addressdo.create_address(item)
        
def address_split(str):
    #address1 = {"address":"1270 Amst Ave, New York NY"}
    #address
    strs=str.split(",")
    dict={}
    dict['street'] = strs[0].strip()
    
    
def address_split(str):
    #address1 = {"address":"1270 Amst Ave, New York NY"}
    #address
    strs=str.split(",")
    dict={}
    dict['street'] = strs[0].strip()
    city_state=strs[1].split()
    dict['state'] = city_state[-1].strip()
    city=""
    for i in city_state[0:-1]:
        city+=i+" "
        dict['city'] = city.strip()
    
    return dict    
    
def lambda_handler(event, context):
    # TODO implement
     
    logger.info(event)
    
    body=event['body']
    logger.info(body)
    body=json.loads(body)
    logger.info(body)
    address=body.get('address',None)
    logger.info(body['address'])
    address=address_split(address)
    logger.info(address)
    err = None
    context = get_context()
    
    item=validate_address(address,context)
    logger.info("Address lookup response2 = " + json.dumps(item,indent=2))
    
    
    
    if item != None:
        addressdo.create_address(item)
    else:
        err = "The address you are trying to create is invalid"
    return respond(err, item)

def respond(err, res=None):
    """

    TODO: We need to flesh this out to handle other error conditions, and to
        return the necessary CORS headers for options.

    :param err: The error that occurred.
    :param res: The response body in JSON.
    :return: A properly formatted API Gateway response.
    """
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else json.dumps(res['address_id']),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': "*",
            'Access-Control-Allow-Origin': "*"
        },
    }