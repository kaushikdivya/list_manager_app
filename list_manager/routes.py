"""
"""

from list_manager import app
from flask import Flask, render_template, request, flash, redirect, url_for, make_response, session, escape
from form import SignUpForm, LoginForm
import authentication as auth
import MySQLdb as msql
import dummy_data
from authentication import BadPasswordError, NoUserExistsError, UserAlreadyExistsError, AccessTokenExpiredError, InvalidAccessTokenError,UserDisabledError
import data_manager as dm
from data_manager import NoListFoundError, NoItemFoundError
import settings

app.config.update({
    'SECRET_KEY': settings.SECRET_KEY,
    'SESSION_COOKIE_NAME': settings.SESSION_COOKIE_NAME
})

#need to check what this cache control is and it's values.
def no_cache(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    response.headers.add('Pragma', 'no-cache')
    return response

def connect_db():
    return msql.connect(
        host=settings.DATABASES['list_manager_db']['host'],
        user=settings.DATABASES['list_manager_db']['user'],
        passwd=settings.DATABASES['list_manager_db']['password'],
        db=settings.DATABASES['list_manager_db']['db_name']
    )

db = connect_db()

@app.route('/login', methods = ['GET', 'POST'])
def login():
    errors = []
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit() == False:
            flash('All fields are required')
            return render_template('login.html', form = form)
        else:
            email = request.form['email']
            password = request.form['password']
            print email , password
            db = connect_db()
            try:
                user_info = auth.authenticate_using_password(email, password, db)
                print user_info
            except BadPasswordError:
                flash("InValid Password")
                response = make_response(redirect(url_for('login')))
                return response
            except NoUserExistsError:
                flash("No User Exists")
                response = make_response(redirect(url_for('login')))
                return response
            session['access_token']= user_info['access_token']
            print "this is sesssion info: %s" %(dir(session))
            response = make_response(redirect(url_for('users')))
            return no_cache(response)


    else:
        return render_template('login.html', form = form)


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit() == False:
            flash('All fields are required')
            return render_template('signup.html', form = form)
        else:
            return "User signed up"
    else:
        return render_template('signup.html', form = form)


@app.route('/home', methods = ['GET'])
def home():
    loginform = LoginForm()

    return render_template('home.html', loginform = loginform)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/users/', methods=['GET'])
def users():
    if 'access_token' in session:
        access_token = session.get('access_token', None)
        db = connect_db ()
        try:
            user_info = auth.authenticate_using_access_token(access_token, db)
            user_id = user_info['id']
            list_of_lists = dm.list_of_list(user_id, db)
        except AccessTokenExpiredError:
            flash("Access Token Expired. Login again")
            return render_template(url_for('login'))
        except InvalidAccessTokenError:
            flash("In Valid Access Token. Login again")
            return render_template(url_for('login'))
        except NoListFoundError:
            flash("No List Created yet.")
            return render_template(url_for('users', user_id = user_id )) #need to check this. as it seems it go in infinite iteration when no list is added by user.


        print type(user_info)
        if request.method == 'GET':
            print  user_info
            response = make_response(render_template('user_home.html', user_info = user_info, lists = list_of_lists, access_token = access_token))
            return no_cache(response)
    else:

        return redirect(url_for('login'))
    # else:
    #     dm.deactive_user(user_info['id'], query_access_token, db)
    #     response_data = {
    #         "meta":{},
    #         "data":{
    #             "users":[
    #                 {
    #                     "authentication" : "Success",
    #                     "name" : user_info['name'],
    #                     "id" : user_info['id'],
    #                     "name" : user_info['name'],
    #                     "delete" : "success"
    #                 }
    #             ]
    #         }
    #     }
    #     status = 200
    #
    # body = json.dumps(response_data)
    # headers = {
    #              'Content-Type' : 'application/json'
    #         }
    # return (body, status, headers)
    #  return render_template('user_home.html', user_data=DUMMY_USERS)



@app.route('/lists/', methods=["POST"])
def new_list():
    #import pdb; pdb.set_trace()
    list_name = request.form['list_name']
    if list_name is not None and len(list_name) == 0:
        list_name = None
    if 'access_token' in session:
        access_token = session.get('access_token', None)
        db = connect_db ()
        try:
            user_info = auth.authenticate_using_access_token(access_token, db)
            user_id = user_info['id']
        except AccessTokenExpiredError:
            flash("Access Token Expired. Login again")
            return redirect(url_for('login'))
        except InvalidAccessTokenError:
            flash("In Valid Access Token. Login again")
            return redirect(url_for('login'))
        if list_name == None:
            flash('Enter the name of the new list')
            return redirect(url_for('users'))
        else:
            dm.create_new_list(list_name, user_id, db)
            return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))


@app.route('/lists/<int:list_id>', methods=['GET', 'POST'])
def lists(list_id):
    if 'access_token' in session:
        print 'list_id: %s, access_token: %s' % (list_id, request.args.get('access_token'))
        access_token = session.get('access_token', None)
        db = connect_db ()
        try:
            user_info = auth.authenticate_using_access_token(access_token, db)
            user_id = user_info['id']
            list_info = dm.fetch_list(list_id, user_id, db)
        except AccessTokenExpiredError:
            flash("Access Token Expired. Login again")
            return redirect(url_for('login'))
        except InvalidAccessTokenError:
            flash("In Valid Access Token. Login again")
            return redirect(url_for('login'))
        except NoListFoundError:
            flash("No List found with this id:%d" %(list_id))
            return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))

    if request.method == 'GET':
        response = make_response(render_template('list_info.html', list_info=list_info))
        return no_cache(response)
    else:
        # import pdb;pdb.set_trace()
        #input_values = map(lambda x:x(0), request.form)
        print request.form
        id = request.form.getlist('item_id')
        non_empty_id = filter(lambda x:x != "", id)
        print non_empty_id
        clean_input = zip(
            request.form.getlist('item_id'),
            request.form.getlist('status'),
            request.form.getlist('fields'),
            request.form.getlist('quantity')
        )
        print clean_input
        for x in clean_input:
            id = x[0]
            status = x[1]
            name = x[2]
            quantity = x[3]
            if id in non_empty_id:
                try:
                    print id
                    list_item_info = dm.update_item(user_id, list_id, id, name, status, quantity, db)

                except NoItemFoundError:
                    flash("No item found")
                    return redirect(url_for('users'))
                except NoListFoundError:
                    flash("No List found with this id:%d" %(list_id))
                    return redirect(url_for('users'))
            else:
                try:

                    list_item_info = dm.add_item_to_list(list_id, user_id, name, status, quantity, db)

                except NoListFoundError:
                    flash("No list found with list_id :%s" % list_id)
                    return redirect(url_for('users'))
        list_info = dm.fetch_list(list_id, user_id, db)
        response = make_response(render_template('list_info.html', list_info=list_info))
        return no_cache(response)


@app.route('/lists/<int:list_id>/items/delete', methods=['POST'])
def delete_item(list_id):
    if 'access_token' in session:
        print 'list_id: %s, access_token: %s' % (list_id, request.args.get('access_token'))
        access_token = session.get('access_token', None)
        db = connect_db ()
        try:
            user_info = auth.authenticate_using_access_token(access_token, db)
            user_id = user_info['id']
            list_info = dm.fetch_list(list_id, user_id, db)
        except AccessTokenExpiredError:
            flash("Access Token Expired. Login again")
            return redirect(url_for('login'))
        except InvalidAccessTokenError:
            flash("In Valid Access Token. Login again")
            return redirect(url_for('login'))
        except NoListFoundError:
            flash("No List found with this id:%d" %(list_id))
            return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))

    try:
        item_id = request.form['item_id']
        dm.delete_item(user_id, list_id, item_id, db)
        list_info = dm.fetch_list(list_id, user_id, db)
    except NoItemFoundError:
        flash("No item found")
        return redirect(url_for('users'))
    except NoListFoundError:
        flash("No List found with this id:%d" %(list_id))
        return redirect(url_for('users'))
    response = make_response(render_template('list_info.html', list_info=list_info))
    return redirect(url_for('lists', list_id = list_id))


@app.route('/logout')
def logout():
    # import pdb; pdb.set_trace()
    if 'access_token' in session:
        access_token = session.get('access_token', None)
        db = connect_db ()
        try:
            user_info = auth.authenticate_using_access_token(access_token, db)
            user_id = user_info['id']
        except AccessTokenExpiredError:
            flash("Access Token Expired. Login again")
            return redirect(url_for('login'))
        except InvalidAccessTokenError:
            flash("In Valid Access Token. Login again")
            return redirect(url_for('login'))
        dm.logout_user(access_token, db)
        session.pop('access_token', None)
        return redirect(url_for('home'))

    else:
        return redirect(url_for('login'))
