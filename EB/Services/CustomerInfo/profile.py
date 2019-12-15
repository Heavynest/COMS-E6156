from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB
from DataAccess.DataObject import ProfileRDB as ProfileRDB
import Middleware.notification as notification
import requests

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


class ProfileService(BaseService):

    required_create_fields = ['uid', 'element_type', 'element_value']
    required_update_fields = ['element_type', 'element_value']
    valid_element_type = ['TELEPHONE', 'ADDRESS', 'EMAIL', 'OTHER']
    valid_element_sub_type = ['HOME', 'MOBILE', 'WORK']

    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()

        self._ctx = ctx

    @classmethod
    def create_profile(cls, profile_info):
        try:
            profile_info = cls.validate_profile(profile_info)
        except Exception as e:
            raise e

        result = ProfileRDB.create_profile_or_update(profile_info=profile_info)

        return result

    # profile by uid
    @classmethod
    def get_by_uid(cls, uid):
        result = {}
        profiles = ProfileRDB.get_by_uid(uid)
        if profiles is None:
            result = "PROFILE NOT EXISTED"
        else:
            email = UsersRDB.query_by_parameters(params={"id": uid}, fields=["email"])
            result["links"] = [{
                "rel": "user",
                "href": "/api/user/" + email[0]["email"],
                "method": "GET"
            }]
            result["profiles"] = profiles
        return result

    @classmethod
    def update_by_uid(cls, new_values):
        try:
            profile_info = cls.validate_profile(new_values)
        except Exception as e:
            raise e
        result = ProfileRDB.create_profile_or_update(profile_info)
        return result

    @classmethod
    def delete_by_uid(cls, uid):
        result = ProfileRDB.delete_by_uid(uid)
        return result

    # profile by query_params
    @classmethod
    def get_profile(cls, query_params):
        result = ProfileRDB.get_profile(query_params)
        return result

    @classmethod
    def validate_profile(cls, profile_info):
        for f in ProfileService.required_create_fields:
            v = profile_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

        if profile_info.get('element_type') not in ProfileService.valid_element_type:
            raise ServiceException(ServiceException.bad_data,
                                   "Invalid element_type: " + profile_info.get('element_type'))

        if profile_info.get('element_subtype') is not None \
                and profile_info.get('element_subtype').upper() not in ProfileService.valid_element_sub_type:
            raise ServiceException(ServiceException.bad_data,
                                   "Invalid element_subtype: " + profile_info.get('element_subtype'))

        if profile_info.get('element_type') == 'EMAIL' and profile_info.get('element_value').find('@') == -1:
            raise ServiceException(ServiceException.bad_data,
                                   "Email looks invalid: " + profile_info.get('element_value'))
        if profile_info.get('element_type') == 'TELEPHONE' and not profile_info.get('element_value').isdigit():
            raise ServiceException(ServiceException.bad_data,
                                   "Phone number looks invalid: " + profile_info.get('element_value'))
        if profile_info.get('element_type') == 'ADDRESS':
            try:
                # TODO
                rsp = 1
                # rsp = requests.get(addressServiceUrl, {'address':profile_info['element_value']})
            except Exception as e:
                raise ServiceException(ServiceException.bad_data,
                                       "Address Service error: " + profile_info.get('element_value'))
            # TODO
            if rsp == 'something':
                addressId = 'addressId'
            else:
                raise ServiceException(ServiceException.bad_data,
                                       "Address looks invalid: " + profile_info.get('element_value'))
            #profile_info['element_value'] = addressId;
        return profile_info
