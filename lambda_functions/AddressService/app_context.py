import os
import boto3
from botocore.exceptions import ClientError
import json

def get_context():

    context = {}

    context["address_url"] = os.environ['starty_config']
    context["auth-id"] = os.environ('auth-id')
    context["auth-token"]=os.environ['auth-token']

    return context