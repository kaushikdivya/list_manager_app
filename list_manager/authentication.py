"""
"""

import hashlib
import uuid
import time
import MySQLdb as msql
from datetime import datetime as dt


SALT_DELIMITER = '$'


class BadPasswordError(Exception):
    pass


class BadAccessTokenError(Exception):
    pass

class NoUserExistsError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class AccessTokenExpiredError(Exception):
    pass

class UserDisabledError(Exception):
    pass

class InvalidAccessTokenError(Exception):
    pass

def create_user_in_db(name, email, password, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select u.id, u.deleted_time from users u where email = %s""" , (email,)) #neeed to add users with deleted_time
    print cur.rowcount
    if cur.rowcount > 0:
        row = cur.fetchone()
        deleted_time = row['deleted_time']
        print deleted_time
        if deleted_time == None:
            raise UserAlreadyExistsError
        else:
            raise UserDisabledError
    else:
        salt = str(uuid.uuid4())
        password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
        salted_password = '%s%s%s' % (salt, SALT_DELIMITER, password_hash)
        insert_status = cur.execute("""insert into users (name, email, password) values (%s,%s,%s)""" , (name, email, salted_password))
        commit_status = db.commit()
        print insert_status, commit_status

def authenticate_using_password(email, password, db):
    stored_password, user_info = get_user_password_from_db(email, db)
    user_id = user_info['id']
    parts = stored_password.split(SALT_DELIMITER)
    print parts
    salt = parts[0]
    password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
    if password_hash == parts[1]:
            print "Password matched successfully"
            access_token = generate_access_token(email,user_id,db)
            user_info['access_token'] = access_token
            print user_info
            return user_info
    # TODO: authetication successful
    else:
        raise BadPasswordError()


# def authenticate_using_access_token(email, password, db):
#     # TODO:
#     pass


def get_user_password_from_db(email, db):
    cur = db.cursor(msql.cursors.DictCursor)
    print email
    rows_count = cur.execute("""select u.id, u.name, u.password, u.email from users u where u.email = %s and u.deleted_time is null""" , (email,))
    if rows_count == 1:
        user_info = cur.fetchone()
        print user_info
        password = user_info.pop('password', None)
        print password
        return password, user_info
    elif rows_count == 0:
        raise NoUserExistsError()
        #Should there be a check for mutiple users with same email though that is taken care at the db side.????????

#need to check how this has to work.
def generate_access_token(email,user_id,db):
    access_token = hashlib.md5('%s%s' % (email,str(time.time()))).hexdigest()
    type(access_token)
    print access_token,user_id
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""insert into access_tokens (user_id, access_token) values (%s, %s )""" , (user_id, access_token))
    db.commit()
    return access_token

def authenticate_using_access_token(access_token, db):
    """
    returns user object if successful, else raises relveant exception
    """

    cur = db.cursor(msql.cursors.DictCursor)
    rows_count = cur.execute("""select a.id, a.user_id, date_add(a.created_time, interval 5 day) as created_time, a.deleted_time from access_tokens a where a.access_token = %s and deleted_time is null""" , (access_token,))

    if rows_count == 0:
        raise InvalidAccessTokenError#????throws expired error only once after that sends invalidaccesstoken error.
    else:
        row = cur.fetchone()
        print type(row)
        now = str(dt.now())
        print type(now)
        current_time = dt.strptime(now, "%Y-%m-%d %H:%M:%S.%f")
        id = row['id']
        user_id = row['user_id']
        expiry_time = row['created_time']
        print expiry_time
        diff_days = (expiry_time - current_time).days
        print diff_days
        deleted_time = row['deleted_time']
        print type(current_time) , type(expiry_time)
        if expiry_time < current_time:
            cur.execute("""update access_tokens set deleted_time = %s where user_id = %s and id = %s""", (current_time, user_id, id))
            db.commit()
        else:
            cur.execute("""select u.id, u.name, u.email from users u where u.id = %s""" , (user_id,))
            user_info = cur.fetchone()
            return user_info
        raise AccessTokenExpiredError



"""
try:
    authenticate_using_password(email, password)
except BadPasswordError:
    # TODO: send error JSON response
    pass
# TODO: send successful login response
"""


