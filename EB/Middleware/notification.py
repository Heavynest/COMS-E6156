import boto3
import json
import os


def publish_it(msg):
    client = boto3.client('sns', region_name="us-east-2", aws_access_key_id=os.environ.get('aws_access_key_id'),
                          aws_secret_access_key=os.environ.get('aws_secret_access_key'))
    txt_msg = json.dumps(msg)
    client.publish(TopicArn="arn:aws:sns:us-east-2:298093020001:E6156CustomerChange",
                   Message=txt_msg)
