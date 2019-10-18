import boto3
import json


def publish_it(msg):

    client = boto3.client('sns', region_name="us-east-2")
    txt_msg = json.dumps(msg)

    client.publish(TopicArn="arn:aws:sns:us-east-2:298093020001:E6156CustomerChange",
                   Message=txt_msg)
