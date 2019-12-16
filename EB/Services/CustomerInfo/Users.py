from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB
import Middleware.notification as notification

# The base classes would not be IN the project. They would be in a separate included package.
# They would also do some things.


class ServiceException(Exception):

    unknown_error   =   9001
    missing_field   =   9002
    bad_data        =   9003

    def __init__(self, code=unknown_error, msg="Oh Dear!"):
        self.code = code
        self.msg = msg


class BaseService():

    missing_field   =   2001

    def __init__(self):
        pass


class UsersService(BaseService):

    required_create_fields = ['last_name', 'first_name', 'email', 'password']
    required_email_fields=['last_name','first_name','password']
    required_delete_fields=['last_name','first_name']

    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()

        self._ctx = ctx

    @classmethod
    def create_user(cls, user_info):
        for f in UsersService.required_create_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

            if f == 'email':
                if v.find('@') == -1:
                    raise ServiceException(ServiceException.bad_data,
                           "Email looks invalid: " + v)

        result = UsersRDB.create_user(user_info=user_info)
        email = user_info.get("email", None)
        msg = {
            "email": email
        }
        try:
            notification.publish_it(msg)
        except Exception as e:
            print(str(e))
        return result

    @classmethod
    def activate_user(cls, email):
        result = UsersRDB.update_by_email({"status": "active"}, email)
        return result

# user_email methods
    @classmethod
    def get_by_email(cls, email, fields=None):
        result = UsersRDB.get_by_email(email, fields)
        if result is None or result["status"].lower() == "deleted" or result["status"].lower() == "pending":
            return None
        return result

    @classmethod
    def update_by_email(cls, new_values, email):
        result = UsersRDB.update_by_email(new_values,email)
        return result

    @classmethod
    def delete_by_email(cls, email):
        result = UsersRDB.update_by_email({"status": "deleted"},email)
        return result

# user_template methods
    @classmethod
    def get_user(cls,user_info):
        result=UsersRDB.get_user(user_info)

        return result

    @classmethod
    def update_email(cls, user_info,email):
        for f in UsersService.required_email_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field, "Missing field = " + f)

        result = UsersRDB.update_email(user_info, email)

        return result

    @classmethod
    def delete_user(cls, user_info):
        for f in UsersService.required_delete_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field, "Missing field = " + f)

        result = UsersRDB.delete_user(user_info)

        return result

# user resource query methods
    @classmethod
    def query_by_parameters(cls, params, fields):
        result = UsersRDB.query_by_parameters(params, fields)

        return result



