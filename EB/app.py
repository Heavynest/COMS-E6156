
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
import json
import jwt
from uuid import uuid4
from datetime import datetime
from flask import Flask, Response, g, request, redirect, url_for
from Context.Context import Context
from Services.CustomerInfo.Users import UsersService as UserService
from Services.CustomerInfo.profile import ProfileService as ProfileService
from Services.RegisterLogin.RegisterLogin import RegisterLoginSvc as RegisterLoginSvc
from functools import wraps
import Middleware.security as security_middleware
import Middleware.notification as notification_middleware


# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###################################################################################################################
#
# AWS put most of this in the default application template.
#
# AWS puts this function in the default started application
# print a nice greeting.


def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username


# AWS put this here.
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
application = Flask(__name__)

# add a rule for the index page. (Put here by AWS in the sample)
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################

_default_context = None
_user_service = None
_registration_service = None
_profile_service = None


def _get_default_context():

    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context()

    return _default_context


def _get_user_service():
    global _user_service

    if _user_service is None:
        _user_service = UserService(_get_default_context())

    return _user_service


def _get_registration_service():
    global _registration_service

    if _registration_service is None:
        _registration_service = RegisterLoginSvc()

    return _registration_service


def _get_profile_service():
    global _profile_service

    if _profile_service is None:
        _profile_service = ProfileService(_get_default_context())

    return _profile_service


def init():

    global _default_context, _user_service, _registration_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)
    _registration_service = RegisterLoginSvc()
    logger.debug("_user_service = " + str(_user_service))


def generate_etag_by_email(email):
    user_service = _get_user_service()
    res = user_service.get_by_email(email)
    etag = security_middleware.generate_etag(res)
    return etag


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):

    path = request.path
    args = dict(request.args)
    data = None
    headers = dict(request.headers)
    method = request.method
    form = request.form

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs =  {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data,
        "form": form
        }

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs


def log_response(method, status, data, txt):

    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2))


@application.route("/api/etag", methods=["GET"])
def get_etag():
    inputs = log_and_extract_input(demo)
    query_params = inputs['query_params']
    email = query_params['email']

    etag = generate_etag_by_email(email)

    return etag


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
def demo(parameter):

    inputs = log_and_extract_input(demo, { "parameter": parameter })

    msg = {
        "/demo received the following inputs" : inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


@application.route("/api/user", methods=["POST"])
@application.route("/api/registrations", methods=["POST"])
def user_register():
    global _user_service

    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    try:

        r_svc = _get_registration_service()

        if inputs["method"] == "POST":

            user_info = dict(inputs["body"])
            user_info['id']=str(uuid4())
            user_info['status']='pending'
            rsp = r_svc.register(user_info)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 201
                rsp_txt = "OK"
                link = rsp_data[0]
                auth = rsp_data[1]
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data=None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/register: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/register", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/user/activate/<email>", methods=["GET"])
def user_activate(email):

    global _user_service

    inputs = log_and_extract_input(demo, {"parameters": email})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        user_service = _get_user_service()

        logger.error("/email: _user_service = " + str(user_service))

        if inputs["method"] == "GET":

            rsp = user_service.activate_user(email)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/login", methods=["POST"])
def login():

    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        logger.error("/api/login: _r_svc = " + str(r_svc))

        if inputs["method"] == "POST":

            # rsp = r_svc.login(inputs['body'])
            rsp, etag = r_svc.login(inputs['body'])

            if rsp is not False:
                rsp_data = "OK"
                rsp_status = 201
                rsp_txt = "CREATED"
            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "NOT AUTHORIZED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            headers = {"Authorization": rsp, "etag": etag}
            full_rsp = Response(json.dumps(rsp_data, default=str), headers=headers,
                                status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/login: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/login", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/user/<email>", methods=["GET", "PUT", "DELETE"])
def user_email(email):

    global _user_service

    inputs = log_and_extract_input(demo, {"parameters": email})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    token = inputs['headers']['Authentication']
    try:
        links_info, operations_info = security_middleware.authorize_api_user_email(email, inputs["method"], token)
    except Exception as e:
        log_msg = "/api/user/<email>: Exception = " + str(e.msg)
        logger.error(log_msg)
        rsp_status = 409
        rsp_txt = e.msg
        return Response(rsp_txt, status=rsp_status, content_type="text/plain")

    try:

        user_service = _get_user_service()

        logger.error("/email: _user_service = " + str(user_service))

        if inputs["method"] == "GET":
            fields = ["last_name", "first_name", "email"]
            rsp = user_service.get_by_email(email, fields)

            if rsp is not None:
                rsp['links'] = links_info
                rsp['operations'] = operations_info
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "PUT":
            user_info = dict(inputs["form"])
            etag0 = inputs['headers']['Etag']
            etag1 = generate_etag_by_email(email)
            if etag0 != etag1:
                rsp_status = 411
                rsp_txt = "User information has been modified."

            else:
                rsp = user_service.update_by_email(user_info, email)
                if rsp is not None:
                    rsp_data = rsp
                    rsp_status = 200
                    rsp_txt = "OK"
                else:
                    rsp_data = None
                    rsp_status = 404
                    rsp_txt = "NOT FOUND"

        elif inputs["method"] == "DELETE":
            rsp = user_service.delete_by_email(email)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/user/<email>/profile", methods=["GET"])
def profile_user(email):
    global _profile_service
    global _user_service

    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:
        user_service = _get_user_service()
        profile_service = _get_profile_service()
        logger.error("/api/user/" + email + "/profile")
        uid = user_service.query_by_parameters(params={"email": email}, fields=["id"])
        uid = uid[0]["id"]
        if inputs["method"] == "GET":

            rsp = profile_service.get_by_uid(uid)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/user/<email>/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/user/<email>/profile: ", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/profile", methods=["GET","POST"])
def profile():
    global _profile_service

    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    try:

        profile_service = _get_profile_service()

        logger.error("/api/profile: _profile_service = " + str(profile_service))
        if inputs["method"] == "POST":
            profile_info = dict(inputs["body"])
            rsp = profile_service.create_profile(profile_info)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "GET":
            query_params = inputs['query_params']
            rsp = profile_service.get_profile(query_params)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/profile: ", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/profile/<uid>", methods=["GET", "PUT", "DELETE"])
def profile_uid(uid):

    global _profile_service

    inputs = log_and_extract_input(demo, {"parameters": uid})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        profile_service = _get_profile_service()

        logger.error("/api/profile/<uid>: _profile_service = " + str(profile_service))

        if inputs["method"] == "GET":

            rsp = profile_service.get_by_uid(uid)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "PUT":
            profile_info = dict(inputs["form"])
            profile_info['uid'] = uid
            rsp = profile_service.update_by_uid(profile_info)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "DELETE":
            rsp = profile_service.delete_by_uid(uid)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/profile/<uid>: " + uid, rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/resource", methods=["GET"])
def resource():
    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    user_service = _get_user_service()

    logger.error("/resource: _user_service = " + str(user_service))

    try:
        user_service = _get_user_service()

        logger.error("/resource: _user_service = " + str(user_service))

        if inputs["method"] == "GET":
            query_params = dict(inputs["query_params"])
            fields = None
            if "fields" in query_params.keys():
                fields = query_params["fields"]
                query_params.pop("fields")

            rsp = user_service.query_by_parameters(query_params, fields)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/resource: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/resource", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/resource/<primary_key>", methods=["GET"])
def resource_with_key(primary_key):
    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    user_service = _get_user_service()

    logger.error("/resource: _user_service = " + str(user_service))

    try:
        user_service = _get_user_service()

        logger.error("/resource: _user_service = " + str(user_service))

        if inputs["method"] == "GET":
            query_params = dict(inputs["query_params"])
            query_params["id"] = primary_key
            fields = None
            if "fields" in query_params.keys():
                fields = query_params["fields"]
                query_params.pop("fields")

            rsp = user_service.query_by_parameters(query_params, fields)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/resource: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/resource", rsp_status, rsp_data, rsp_txt)

    return full_rsp


logger.debug("__name__ = " + str(__name__))
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.run(port=5033)
