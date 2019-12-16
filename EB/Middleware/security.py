import jwt
from Context.Context import Context
from time import time
import json
from urllib.parse import urlparse
import hashlib
_context = Context.get_default_context()


class ActionException(Exception):

    unknown_error   =   2001
    unproved_action  =   2002

    def __init__(self, code=unknown_error, msg="NOT APPROVED."):
        self.code = code
        self.msg = msg


class TokenException(Exception):

    unknown_error   =   2101

    def __init__(self, code=unknown_error, msg="INVALID TOKEN."):
        self.code = code
        self.msg = msg


def generate_etag(user_info):
    x = json.dumps(user_info, sort_keys = True).encode("utf-8")
    etag = hashlib.md5(x).hexdigest()
    return etag


def hash_password(pwd):
    global _context
    h = jwt.encode(pwd, key=_context.get_context("JWT_SECRET"))
    h = str(h)
    return h


def generate_token(info):

    info["timestamp"] =  time()
    email = info['email']

    if email == 'admin@admin':
        info['role']='admin'
    else:
        info['role']='student'

    info['created'] = str('created')

    h = jwt.encode(info, key=_context.get_context("JWT_SECRET"))
    h = h.decode("utf-8")
    return h


def authorize(url, method, token):
    # Extract user information from url. Determine whether the methond should be approved.
    u = urlparse(url)
    action = u[2].split("/")

    approve_anyuser = ["GET", "PUT"]
    approve_admin = ["GET", "PUT", "DELETE"]
    approve_onlyposter = ["POST"]
    if token:
        try:
            info = jwt.decode(token, key="jwt-secret")
        except(jwt.DecodeError, jwt.ExpiredSignatureError):
            return json.response({'message': 'Token is not valid'})
    email = ""
    uid = ""
    for i in action:
        if "@" in i:
            email = i
            break
        if "-" in i:
            uid = i
            break

    if method in approve_onlyposter:
        if email == token['email'] or uid == token["uid"]:
            info['operations'] = approve_onlyposter
        else:
            raise (ActionException(ActionException.unproved_action))
    elif method in approve_admin:
        if info['role'] != 'admin':
            raise (ActionException(ActionException.unproved_action))
        else:
            info['operations'] = approve_admin
    else:
        info["operations"] = approve_anyuser

    h = jwt.encode(info, key=_context.get_context("jwt-secret"))
    h = str(h)

    return h


def authorize_api_user_email(email, method, token):
    # Extract user information from url. Determine whether the methond should be approved.
    anyuser = ["GET"]
    self_only = ["PUT"]
    admin_only = ["DELETE"]
    links_info = None
    operations_info = None

    try:
        info = jwt.decode(token, key="cat")
    except(jwt.DecodeError, jwt.ExpiredSignatureError):
        raise TokenException()

    if method in admin_only:
        if info['role'] != 'admin':
            raise (ActionException(ActionException.unproved_action))
    elif method in self_only:
        if email != info['email']:
            raise (ActionException(ActionException.unproved_action))

    if method == "GET":
        links_info = [{
            "rel": "profile",
            "href": "/api/user/" + email + "/profile",
            "method": "GET"
        }]
        operations_info = {
            "role": info["role"],
            "api": "/api/user/" + email,
            "operations": anyuser
        }
        if email == info['email']:
            operations_info["operations"] += self_only
        if info['role'] == 'admin':
            operations_info["operations"] += admin_only

    return links_info, operations_info
