import json
import boto3
from botocore.exceptions import ClientError
import jwt.jwt as jwt
from botocore.vendored import requests
import logging
import os

# Note: The logging levels should come from a config/property file and not be hard coded.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)

_secret = "jwt-secret"
# def send_activation2(email):
    
#     msg = {"email": email}
#     logger.info("Encoding " + json.dumps(msg))
#     tok_byte = jwt.encode(msg, key=_secret)
    
#     tok_str = tok_byte.decode("utf-8")
#     logger.info("Encoded = " + tok_str)
#     logger.info("https://e28s1mkwi2.execute-api.us-east-2.amazonaws.com/default/EmailVerification?token=" + tok_str)
    
#     dec = jwt.decode(tok_str, key=_secret)
#     logger.info("Decoded =  " + json.dumps(dec))

def send_activation(email):
    logger.info("###################")
    test_stuff = {"email": email}
    logger.info("Encoding " + json.dumps(test_stuff))
    tok = jwt.encode(test_stuff, key=_secret)
    logger.info("Encoded = " + str(tok))
    tok=tok.decode("utf-8")
    # dec = jwt.decode(tok, key=_secret)
    # logger.info("Decoded =  " + json.dumps(dec))
    
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "E6156-sender <xiao-chao-cool@hotmail.com>"
    
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    
    RECIPIENT = email
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    # SUBJECT = "Amazon SES Test (SDK for Python)"
    SUBJECT = "E6156-registration: Activate your account!"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Click the following link to activate your account!\r\n")
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Click the following link to activate your account!</h1>
      <p>
        <a href='https://6omesnmip9.execute-api.us-east-2.amazonaws.com/start/?token={}'>Activate Now!</a></p>
    </body>
    </html>
                """.format(tok)

    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    # try:
    client = boto3.client('ses',region_name=AWS_REGION)
    # except Exception as e:
    #     logger.info(str(e))
    # Try to send the email.
    logger.info("client built!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print("hhhhhhhhhhhhh-------------------")
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return
    
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
        'body': err if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

URL="http://E6156P1-env.swdckad4ii.us-east-2.elasticbeanstalk.com/api/user/activate/"

def lambda_handler(event, context):
    logger.info("---start---")
    logger.info(jwt.encode({"e":"popopo"}, key=_secret))
    logger.info("\nEvent = " + json.dumps(event, indent=2) + "\n")

    # Some introspection of event allows figuring out where it came from.
    records = event.get("Records", None)
    method = event.get("httpMethod", None)
    if records is not None:
        logger.info("I got an SNS event.")
        logger.info("Records = " + json.dumps(records))
        message = json.loads(records[0]["Sns"]["Message"])
        email = message["email"]
        logger.info(email)
        send_activation(email)
    elif method is not None:
        logger.info("I got an API GW proxy event.")
        logger.info("httpMethod = " + method + "\n")
        token=event["queryStringParameters"]
        token=token["token"]
        logger.info("token: " + token + "\n")
        try:
            decryption=jwt.decode(token, _secret)
            logger.info("Decoded =  " + json.dumps(decryption))
        except Exception as e:
            logger.info("Decryption Error: " + str(e) + "\n")
            return respond("Decryption Err")
        try:
            logger.info(decryption["email"])
            rsp = requests.get(URL+decryption["email"])
            if rsp.json() == 0:
                return respond("Not a valid activation: Not a valid user or the user has been activated.")
            logger.info("Activation succeed.")
            logger.info("rsp:" + str(rsp.json()))
            return respond(None,rsp.json())
        except Exception as e:
            logger.info(str(e))
            logger.info("Activation failed!")
            return respond("Email not found")
    else:
        logger.info("Not sure what I got.")

    response = respond(None, event)
    return response

