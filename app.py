from db import DB_NAME, Base, User, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from dry import randomString

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

engine = create_engine('sqlite:///{}.db'.format(DB_NAME))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# User Login


@app.route('/login/')
def login():
    state = randomString()
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return "success"


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}'.format(
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?access_token={}&fields=name,id,email'.format(
        token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)

    print(data)

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    url = 'https://graph.facebook.com/v3.2/me/picture/?access_token={}&redirect=0&height=200&width=200'.format(
        token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)

    print(data)

    login_session['picture'] = data['data']['url']

    user_id = getUserId(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return "success"


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/{}/permissions'.format(facebook_id)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


@app.route('/disconnect/')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        return redirect(url_for('catalog'))
    else:
        return redirect(url_for('catalog'))


def getUserId(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# JSON APIs Endpoints

@app.route('/api/catalog/')
def apiCatalog():
    session = DBSession()
    categories = session.query(Category).filter_by().all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/api/categories/<int:category_id>/')
def apiCategory(category_id):
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Category=category.serialize, Items=[i.serialize for i in items])


@app.route('/api/items/<int:item_id>/')
def apiItem(item_id):
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# Pages

@app.route('/redirect/')
def destination():
    if login_session.get('destination'):
        dest = login_session['destination']
        del login_session['destination']

        if dest.get('category_name'):
            if dest.get('item_name'):
                return redirect(url_for(dest['route'],
                                        category_name=dest['category_name'],
                                        item_name=dest['item_name']))
            else:
                return redirect(url_for(dest['route'],
                                        category_name=dest['category_name']))
        else:
            return redirect(url_for(dest['route']))

    else:
        return redirect(url_for('catalog'))


@app.route('/')
@app.route('/catalog/')
def catalog():
    session = DBSession()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    new_items = session.query(Item).order_by(desc(Item.id)).limit(10).all()

    username = login_session.get('username')
    if username is None:
        authorized_user = False
    else:
        authorized_user = True

    return render_template('catalog.html', authorized_user=authorized_user, username=username, categories=categories, new_items=new_items)


@app.route('/catalog/<category_name>/')
def category(category_name):
    session = DBSession()
    category = session.query(Category).filter_by(
        name=category_name).first()

    if category is None:
        message = "No such category exists!"
        return render_template('error.html', message=message, redirect='catalog')

    items = session.query(Item).filter_by(
        category_id=category.id).order_by(desc(Item.id)).limit(10).all()

    username = login_session.get('username')
    if username is None:
        authorized_user = False
    else:
        authorized_user = True

    return render_template('category.html', authorized_user=authorized_user, username=username, category=category, items=items)


@app.route('/catalog/<category_name>/<item_name>/')
def item(category_name, item_name):
    session = DBSession()
    category = session.query(Category).filter_by(
        name=category_name).first()

    if category is None:
        message = "No such category exists!"
        return render_template('error.html', message=message, redirect='catalog')

    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).first()

    if item is None:
        message = "No such item exists in this category!"
        return render_template('error.html', message=message, redirect='catalog')

    username = login_session.get('username')
    if username is None:
        authorized_user = False
        creator = False
    else:
        authorized_user = True
        if login_session['user_id'] != item.user_id:
            creator = False
        else:
            creator = True

    return render_template('item.html', authorized_user=authorized_user, creator=creator, username=username, item=item)


@app.route('/catalog/create_item/', methods=['GET', 'POST'])
def itemCreate():
    session = DBSession()

    username = login_session.get('username')
    if username is None:
        authorized_user = False
    else:
        authorized_user = True

    if request.method == 'POST':
        if authorized_user:
            cat_id = session.query(Category).filter_by(
                name=request.form['category']).one().id

            newItem = Item(name=request.form['name'], description=request.form['description'],
                           image_url=request.form.get('image_url'), category_id=cat_id,
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()

            return redirect(url_for('catalog'))
        else:
            login_session['destination'] = {'route': 'itemCreate'}

            message = "You must be logged in to create an item!"
            return render_template('error.html', message=message, redirect='login')

    elif request.method == 'GET':
        categories = session.query(Category).all()

        if authorized_user:
            return render_template('item_create.html', authorized_user=authorized_user, username=username, categories=categories)
        else:
            login_session['destination'] = {'route': 'itemCreate'}

            message = "You must be logged in to create an item!"
            return render_template('error.html', message=message, redirect='login')


@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def itemUpdate(category_name, item_name):
    session = DBSession()
    category = session.query(Category).filter_by(
        name=category_name).first()

    if category is None:
        message = "No such category exists!"
        return render_template('error.html', message=message, redirect='catalog')

    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).first()

    if item is None:
        message = "No such item exists in this category!"
        return render_template('error.html', message=message, redirect='catalog')

    username = login_session.get('username')
    if username is None:
        authorized_user = False
        creator = False
    else:
        authorized_user = True
        if login_session['user_id'] != item.user_id:
            creator = False
        else:
            creator = True

    if request.method == 'POST':
        if authorized_user:
            if creator:               
                name = request.form.get('name')
                description = request.form.get('description')
                image_url = request.form.get('image_url')
                item_category = request.form.get('category')

                if name:
                    item.name = name
                
                if description:
                    item.description = description

                if image_url:
                    item.image_url = image_url

                if item_category:
                    cat_id = session.query(Category).filter_by(
                        name=item_category).one().id
                    item.category_id = cat_id
                session.add(item)
                session.commit()

                return redirect(url_for('catalog'))
            else:
                message = "Only the creator of an item can edit it!"
                return render_template('error.html', message=message, redirect='catalog')
        else:
            login_session['destination'] = {'route': 'itemUpdate',
                                            'category_name': category_name,
                                            'item_name': item_name}

            message = "You must be logged in to edit an item!"
            return render_template('error.html', message=message, redirect='login')

    elif request.method == 'GET':
        categories = session.query(Category).all()

        if authorized_user:
            if creator:
                return render_template('item_update.html', authorized_user=authorized_user, username=username, categories=categories, item=item)
            else:
                message = "Only the creator of an item can edit it!"
                return render_template('error.html', message=message, redirect='catalog')
        else:
            login_session['destination'] = {'route': 'itemUpdate',
                                            'category_name': category_name,
                                            'item_name': item_name}

            message = "You must be logged in to edit an item!"
            return render_template('error.html', message=message, redirect='login')


@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def itemDelete(category_name, item_name):
    session = DBSession()
    category = session.query(Category).filter_by(
        name=category_name).first()

    if category is None:
        message = "No such category exists!"
        return render_template('error.html', message=message, redirect='catalog')

    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).first()

    if item is None:
        message = "No such item exists in this category!"
        return render_template('error.html', message=message, redirect='catalog')

    username = login_session.get('username')
    if username is None:
        authorized_user = False
        creator = False
    else:
        authorized_user = True
        if login_session['user_id'] != item.user_id:
            creator = False
        else:
            creator = True

    if request.method == 'POST':
        if authorized_user:
            if creator:
                session.delete(item)
                session.commit()

                return redirect(url_for('catalog'))
            else:
                message = "You must be the creator of an item to delete it!"
                return render_template('error.html', message=message, redirect='catalog')
        else:
            login_session['destination'] = {'route': 'itemDelete',
                                            'category_name': category_name,
                                            'item_name': item_name}

            message = "You must be logged in to delete an item!"
            return render_template('error.html', message=message, redirect='login')

    elif request.method == 'GET':
        if authorized_user:
            if creator:
                return render_template('item_delete.html', authorized_user=authorized_user, username=username, item=item)
            else:
                message = "You must be the creator of an item to delete it!"
                return render_template('error.html', message=message, redirect='catalog')
        else:
            login_session['destination'] = {'route': 'itemDelete',
                                            'category_name': category_name,
                                            'item_name': item_name}

            message = "You must be logged in to delete an item!"
            return render_template('error.html', message=message, redirect='login')


if __name__ == '__main__':
    app.secret_key = randomString()
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
