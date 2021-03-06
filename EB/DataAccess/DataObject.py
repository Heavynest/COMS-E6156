import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err


class DataException(Exception):

    unknown_error   =   1001
    duplicate_key   =   1002

    def __init__(self, code=unknown_error, msg="Something awful happened."):
        self.code = code
        self.msg = msg

class BaseDataObject(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls, data):
        pass


class UsersRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def create_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_insert(table_name="users", row=user_info)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = user_info['id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

#user_email methods
    @classmethod
    def get_by_email(cls, email, fields):
        try:
            sql, args = data_adaptor.create_select(table_name="users", template={"email":email}, fields=fields)
            res, data = data_adaptor.run_q(sql, args)
        except Exception as e:
            raise DataException()

        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def update_by_email(cls, new_values, email):

        try:
            sql, args = data_adaptor.create_update(table_name="users",new_values=new_values,template={"email":email})
            res, data = data_adaptor.run_q(sql, args)
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return res

# user_template methods
    @classmethod
    def get_user(cls, user_info):
        try:
            sql, args = data_adaptor.create_select(table_name="users",template=user_info)
            res, data = data_adaptor.run_q(sql, args)
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return res

    @classmethod
    def delete_user(cls,user_info):
        try:
            sql, args = data_adaptor.create_update(table_name="users",new_values={"status":"deleted"},template=user_info)
            res, data = data_adaptor.run_q(sql, args)
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return res


# user resource query methods
    @classmethod
    def query_by_parameters(cls, params, fields):
        try:
            sql, args = data_adaptor.create_select(table_name="users", template=params, fields=fields)
            res, data = data_adaptor.run_q(sql, args)
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return data



class ProfileRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def create_profile_or_update(cls, profile_info):
        try:
            sql, args = data_adaptor.create_insert(table_name="profile", row=profile_info)
            sql += ' on duplicate key update element_value = values(element_value)'
            res, data = data_adaptor.run_q(sql, args)
            result = profile_info['uid']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    # profile by uid
    @classmethod
    def get_by_uid(cls, uid):
        sql = "select * from e6156.profile where uid=%s"
        res, data = data_adaptor.run_q(sql=sql, args=uid, fetch=True)
        return data

    @classmethod
    def delete_by_uid(cls, uid):
        try:
            sql = data_adaptor.create_delete(table_name="profile",template={"uid":uid})
            res, data = data_adaptor.run_q(sql, args=uid)
        except Exception as e:
            raise DataException()

        return res

    # profile by query_params
    @classmethod
    def get_profile(cls, profile_info):
        try:
            sql, args = data_adaptor.create_select(table_name="profile",template=profile_info)
            res, data = data_adaptor.run_q(sql, args)
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return data


