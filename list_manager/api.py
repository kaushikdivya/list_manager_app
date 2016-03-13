"""
sample flask API
"""

import json

from flask import Flask
from flask import request
import authentication as auth
import MySQLdb as msql
import dummy_data
from authentication import BadPasswordError, NoUserExistsError, UserAlreadyExistsError, AccessTokenExpiredError, InvalidAccessTokenError,UserDisabledError
import data_manager as dm
from data_manager import NoListFoundError, NoItemFoundError
import settings

app = Flask(__name__)
app.debug = True



@app.route('/')
def hello():
    html_string="""
    <body>
        <h1>Hello World</h1>
    </body>"""
    return html_string

def connect_db():
    return msql.connect(
        host=settings.DATABASES['list_manager_db']['host'],
        user=settings.DATABASES['list_manager_db']['user'],
        passwd=settings.DATABASES['list_manager_db']['password'],
        db=settings.DATABASES['list_manager_db']['db_name']
    )

#def authenticate_accesstoken():

# def users_existence():
#     username = request.form['username']
#     print username, dummy_data.existing_users
#     for x in dummy_data.existing_users:
#         print x, x['username']
#         if x['username'] == username:
#             return x
#     return None
@app.route('/users/login', methods=['POST'])
def users_login():
    #import pdb; pdb.set_trace()

    # that's how you access query parameters
    #access_token = request.args.get('access_token', '')

    # that's how you determine what HTTP method is being called

    #import traceback; traceback.print_exc();

    if request.method == 'POST':
        # that's how you access request HTTP headers
        #if not request.headers['Content-Type'].lower().startswith('application/json'):
          #  raise ValueError('POST and PUT accept only json data')
        email = request.form['email']
        password = request.form['password']
        print email , password
        db = connect_db()
        try:
            user_info = auth.authenticate_using_password(email, password, db)
            print user_info
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                        "authentication" : 'Sucess',
                        "name" : user_info['name'],
                        "id" : user_info['id'],
                        "email" : user_info['email'],
                        "access_token" : user_info['access_token']
                    }]
                }
            }
            status = 200
        except BadPasswordError:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                    "status" : "Failed",
                    "message" : "Wrong password"
                    }]
                }
            }
            status = 400

        except NoUserExistsError:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                        "status" : "Failed",
                        "message" : "User doesn't exists. Sign up please"
                    }]
                }
            }
            status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)

        # that's how you access request body
        #data = request.json['data']

@app.route('/users' , methods=['POST'])
def users():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    db = connect_db()
    try:
        auth.create_user_in_db(name, email, password, db)
        response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                        "status" : "Sucess",
                        "message" : "User has been created. Login now"
                    }]
                }
            }
        status = 200
    except UserAlreadyExistsError:
        response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                    "status" : "Failed",
                    "message" : "User already exists with email : %s. Login or reset password" %(email)
                    }]
                }
            }
        status = 400
    except UserDisabledError:
        response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                        "status" : "Failed",
                        "message" : "User with the email : %s already exists but is disabled for now." % (email)
                    }]
                }
        }
        status = 400
    headers = {
        'Content-Type' : 'application/json'
    }
    body = json.dumps(response_data)
    return (body, status, headers)

#response body for user info
@app.route('/users/<int:user_id>', methods=['GET', 'DELETE'])
def user_info(user_id):

    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)


    print type(user_info)
    if request.method == 'GET':
        print  user_info
        response_data = {
            "meta":{},
            "data":{
                "users":[
                    {
                        "authentication" : 'Sucess',
                        "name" : user_info['name'],
                        "id" : user_info['id'],
                        "email" : user_info['email'],
                    }
                ]
            }
        }
        status = 200
    else:
        dm.deactive_user(user_info['id'], query_access_token, db)
        response_data = {
            "meta":{},
            "data":{
                "users":[
                    {
                        "authentication" : "Success",
                        "name" : user_info['name'],
                        "id" : user_info['id'],
                        "name" : user_info['name'],
                        "delete" : "success"
                    }
                ]
            }
        }
        status = 200

    body = json.dumps(response_data)
    headers = {
                 'Content-Type' : 'application/json'
            }
    return (body, status, headers)

# PUT http request on logout
@app.route('/users/logout', methods = ['PUT'])
def logout():
    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
        user_id = user_info['id']
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)

    #Logout user after authentication via access token
    dm.logout_user(query_access_token, db)
    response_data = {
        "meta" : {},
        "data" : {
            "users" : [
                {
                    "status" : "user logged out"
                }
            ]
        }
    }
    status = 200
    body = json.dumps(response_data)
    headers = {
        'Content-Type' : 'application/json'
    }
    return (body, status, headers)


# POST and GET http request on /lists
@app.route('/lists', methods = ['POST', 'GET'])
def lists():

    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
        user_id = user_info['id']
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    #All list under that user
    if request.method == 'GET':
        try:
            list_of_lists = dm.list_of_list(user_id, db)
            print list_of_lists
        except NoListFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No List found of this user"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 200
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        response_data = {
            "meta" : {},
            "data" : {
                "users" : user_info,
                "lists" : list_of_lists
            }
        }
        body = json.dumps(response_data)
        status = 200
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)
    else:
        # Add new list(how to handle request data)
        data = request.json['data']
        list_name = data['lists'][0]['name']
        list_info = list(dm.create_new_list(list_name, user_id, db))
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : list_info
            }
        }
        body = json.dumps(response_data)
        status = 200
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)



#change name of the existing list
@app.route('/lists/<int:list_id>', methods=['PUT', 'GET', 'DELETE'])
def change_list_name(list_id):

    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
        user_id = user_info['id']
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    if request.method == 'PUT':
        print request.json
        data = request.json['data']
        new_name = data['lists'][0]['name']
        try:
            list_info = dm.change_list_name(list_id, new_name, user_id, db)
        except NoListFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No List found of this user"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 400
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        response_data = {
                "meta" : {},
                "data" : {
                    "lists" : list_info
                }
            }

        status = 200
    elif request.method == 'GET': #fetching list info as per the list id
        try:
            list_info = dm.fetch_list(list_id, user_id, db)
        except NoListFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No List found of this user"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 400
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : list_info
            }
        }
        status = 200
    else: # deleting entire list from the user's list
        try:
            dm.delete_list(list_id, user_id, db)
        except NoListFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No List found of this user"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 400
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [{
                    "message" : "List deleted from the user's list"
                }]
            }
        }
        status = 200
    headers = {
        'Content-Type' : 'application/json'
    }
    body = json.dumps(response_data)
    return (body,status,headers)

#Adding item to a list
@app.route('/lists/<int:list_id>/items', methods = ['POST'])
def add_item(list_id):

    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
        user_id = user_info['id']
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    try:
        data = request.json['data']
        name = data['lists'][0]['items'][0]['name']
        status = data['lists'][0]['items'][0]['status']
        quantity = data['lists'][0]['items'][0]['quantity']
        list_item_info = dm.add_item_to_list(list_id, user_id, name, status, quantity, db)
    except NoListFoundError:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [{
                    "message" : "No List found of this user"
                }]
            }
        }
        body = json.dumps(response_data)
        status = 400
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)
    response_data = {
        "meta" : {},
        "data" : {
            "lists" : [
                list_item_info
            ]
        }
    }
    status = 400
    body = json.dumps(response_data)
    headers = {
        "Content-Type" : 'application/json'
    }
    return (body,status,headers)

#PUT and DELETE http request on items
@app.route('/lists/<int:list_id>/items/<int:item_id>', methods = ['PUT' , 'DELETE'])
def Item_modification(list_id, item_id):
    query_access_token = request.args.get('access_token')
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(query_access_token, db)
        user_id = user_info['id']
    except AccessTokenExpiredError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [{
                    "authentication" : 'Expired',
                    "message" : "Access token Expired"
                }]
            }
        }
        status = 401
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)
    except InvalidAccessTokenError:
        response_data = {
            "meta" : {},
            "data" : {
                "users" : [
                    {
                        "message" : "Invalid access token : %s" % (query_access_token)
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)

    #Change requests for name and status of an item
    if request.method == 'PUT':
        data = request.json['data']['lists'][0]['items'][0]
        print data
        if 'name' in data:
            try:
                list_item_info = dm.change_item_name(user_id, list_id, item_id, data['name'], db)
            except NoItemFoundError:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "lists" : [{
                            "message" : "No Item found of this list"
                        }]
                    }
                }
                body = json.dumps(response_data)
                status = 400
                headers = {
                    "Content-Type" : 'application/json'
                }
                return (body,status,headers)
            except NoListFoundError:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "lists" : [{
                            "message" : "No List found of this user"
                        }]
                    }
                }
                body = json.dumps(response_data)
                status = 400
                headers = {
                    "Content-Type" : 'application/json'
                }
                return (body,status,headers)
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [
                        list_item_info
                    ]
                }
            }
            status = 400
            body = json.dumps(response_data)
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        else:
            try:
                list_item_info = dm.change_item_status(user_id, list_id, item_id, data['status'], db)
            except NoItemFoundError:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "lists" : [{
                            "message" : "No Item found of this list"
                        }]
                    }
                }
                body = json.dumps(response_data)
                status = 400
                headers = {
                    "Content-Type" : 'application/json'
                }
                return (body,status,headers)
            except NoListFoundError:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "lists" : [{
                            "message" : "No List found of this user"
                        }]
                    }
                }
                body = json.dumps(response_data)
                status = 400
                headers = {
                    "Content-Type" : 'application/json'
                }
                return (body,status,headers)
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [
                        list_item_info
                    ]
                }
            }
            status = 400
            body = json.dumps(response_data)
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)

    else:
        try:
            dm.delete_item(user_id, list_id, item_id, db)
        except NoListFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No List found of this user"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 400
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        except NoItemFoundError:
            response_data = {
                "meta" : {},
                "data" : {
                    "lists" : [{
                        "message" : "No Item found of this list"
                    }]
                }
            }
            body = json.dumps(response_data)
            status = 400
            headers = {
                "Content-Type" : 'application/json'
            }
            return (body,status,headers)
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "items": {
                            "message" : "Item deleted from the list"
                        }
                    }
                ]
            }
        }
        status = 400
        body = json.dumps(response_data)
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)






if __name__ == "__main__":
    app.run()
