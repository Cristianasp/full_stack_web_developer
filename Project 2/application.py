#!/usr/bin/env python
'''
Udacity Nanodegree FullStack Web developer
Project Item Catalog
Author: Cristiana Parada 
Catalog menu -  main application
'''

###############################################################################


'''from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response'''
from flask import session as login_session
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash,
                   make_response)

import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import logging

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from catalog_database import User, Category, Item

###############################################################################
''' General Information'''
###############################################################################


app = Flask(__name__)

CLIENT_ID = json.loads(
                open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog Menu Application"

# Connect to Database and create database session, ignoring thread
engine = create_engine('sqlite:///Catalog.db',
                       connect_args={'check_same_thread': False})
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

###############################################################################
''' USER AND LOGIN SESSSION '''
###############################################################################


@app.route('/login')
def showLogin():
    ''' Login - Create anti-forgery state token '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

###############################################################################


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    ''' Authorization via Facebook. '''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    logger.info("Facebook access token received %s " % access_token)
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'\
          'grant_type=fb_exchange_token&client_id=%s&'\
          'client_secret=%s&fb_exchange_token=%s' % (
           app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
    Due to the formatting for the result from the server token exchange we have
    to split the token first on commas and select the first index which gives
    us the key : value for the server access token then we split it on colons
    to pull out the actual token value and replace the remaining quotes with
    nothing so that it can be used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me? '\
          'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    logger.info("url sent for API access:%s" % url)
    logger.info("API JSON result: %s" % result)
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&'\
          'redirect=0&height=200&width=200''' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += 'Welcome, '
    output += login_session['username']
    output += '!'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;"'
    output += '"border-radius: 75px;-webkit-border-radius: 75px;"'
    output += '"-moz-border-radius: 75px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output

###############################################################################


@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' Authorization via Google.'''
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
        logger.warn("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                    'Current user is already connected.'), 200)
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

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += 'Welcome, '
    output += login_session['username']
    output += '!'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 75px;"'
    output += '"-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    logger.info("Google sign-in done for %s" % login_session['email'])
    return output

###############################################################################


@app.route('/logout')
def disconnect():
    ''' Logout the user and reset session information.'''
    logger.info("Disconecting user... ")
    # checks if there is a provider registered in login_session
    if login_session:

        if login_session['provider'] == 'google':
            # Only disconnect a connected user.
            access_token = login_session.get('access_token')
            if access_token is None:
                response = make_response(
                    json.dumps('Current user not connected.'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
            url = 'https://accounts.google.com/o/oauth2/revoke?'\
                  'token=%s' % access_token
            h = httplib2.Http()
            result = h.request(url, 'GET')[0]

        if login_session['provider'] == 'facebook':
            facebook_id = login_session['facebook_id']
            # The access token must me included to successfully logout
            access_token = login_session['access_token']
            url = 'https://graph.facebook.com/%s/permissions?'\
                  'access_token=%s' % (facebook_id, access_token)
            h = httplib2.Http()
            result = h.request(url, 'DELETE')[1]

    login_session.clear()
    return redirect(url_for('showCategories'))

###############################################################################
''' User Helper Functions - Database connection
https://github.com/CooledCoffee/sqlalchemy-dao
To keep your implementation easier for maintenance, please consider to separate
the DB helpers from the endpoint/api implementation.
There is a concept called DAO (Data Access Object) may help you why we should
do so:
In computer software, a data access object (DAO) is an object that provides an
abstract interface to some type of database or other persistence mechanism.
By mapping application calls to the persistence layer, DAO provide some
specific data operations without exposing details of the database.
DAO is a useful concept for database query and information hiding, please
consider to separate the relevant functions into a helper file and make the
import when necessary.
Please look at https://github.com/CooledCoffee/sqlalchemy-dao for a direct
example in terms of using the DAO concept for building up the sqlalchemy-dao
python library, it might be useful for you to deal with the user's table.'''
###############################################################################


def createUser(login_session):
    ''' Create an user in the database'''
    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'],
                   provider=login_session['provider'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    ''' Retrieves user information given an ID '''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    ''' Retrieves user ID given an email address'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

###############################################################################
'''CATEGORIES, ITEMS, JSON'''
###############################################################################


@app.route('/JSON')
@app.route('/catalog.json')
def ItemsJSON():
    ''' Full catalog output in json format'''
    result = session.query(Item.name.label("Item_Name"),
                           Item.description.label("Item_Description"),
                           Category.name.label("Category_Name")).join(
                           Item, Item.category_id == Category.id).all()
    algo = []
    for r in result:
        algo = algo + [[dict({'Item_Name': r[0], 'Item_Description': r[1],
                        'Category_Name': r[2]})]]
    return jsonify(result=algo)
# reviewer recomended do use json.load()
# https://docs.python.org/3/library/json.html
###############################################################################
'''
It's better to use .one_or_none() instead of .one(); as .one() raises
sqlalchemy.orm.exc.NoResultFound if the query selects no rows.
While .one_or_none() returns None if the query selects no rows.
With no rows found using .one(), E.g:
>>> user = query.filter(User.id == 99).one()
Traceback (most recent call last):
...
NoResultFound: No row was found for one()
With no rows found using .one_or_none(), E.g:
>>> user = query.filter(User.id == 99).one_or_none()
<<< None
Reference:
http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.
Query.one_or_none
.one_or_none() is like .one(), except that if no results are found,
it doesn’t raise an error; it just returns None.
Like .one(), however, it does raise an error if multiple results are found.
'''

@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def ItemJSON(category_name, item_name):
    ''' One chosen item from a chosen category in json format'''
    result = session.query(Item).filter_by(name=item_name).one_or_none()
    algo = [[dict({'Item_Name': result.name,
                   'Item_Description': result.description})]]
    return jsonify(result=algo)

###############################################################################


@app.route('/catalog/<string:category_name>/JSON')
@app.route('/catalog/<string:category_name>/items/JSON')
def CategoryJSON(category_name):
    ''' Items of one choosen category in json format'''
    category = session.query(Category).filter_by(name=category_name).one()
    result = session.query(Item.name.label("Item_Name"),
                           Item.description.label("Item_Description"),
                           Category.name.label("Category_Name")).join(
                           Item, Item.category_id == Category.id).filter_by(
                           category_id=category.id).all()
    algo = []
    for r in result:
        algo = algo + [[dict({'Item_Name': r[0], 'Item_Description': r[1],
                        'Category_Name': r[2]})]]
    return jsonify(result=algo)

###############################################################################


@app.route('/')
def showCategories():
    ''' Initial page that shows categories and recently added items. '''
    category = session.query(Category).all()
    items = session.query(Item.name.label("iname"), Item.description,
                          Category.name.label("cname")).join(
                          Item, Item.category_id == Category.id).limit(10)
    return render_template('items.html', items=items, categories=category,
                           login_session=login_session)

###############################################################################


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showItems(category_name):
    ''' Show items of a choosen category.'''
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    items = session.query(Item). filter_by(
                category_id=category.id).all()
    return render_template('categoryitems.html',
                           items=items,
                           category=category,
                           categories=categories,
                           login_session=login_session)

###############################################################################


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    ''' Show item detail information.'''
    item = session.query(Item).filter_by(name=item_name).one()
    if item.created_by == login_session['user_id']:
        authorized = True
    else:
        authorized = False
    return render_template('item.html', item=item,
                           login_session=login_session,
                           autho=authorized)

###############################################################################


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    ''' Create an new item of a choosen category.'''
    if request.method == 'POST':
        if login_session:
            if login_session['username']:
                logger.info(request.form)
                category = session.query(Category).filter_by(
                    name=request.form['category_name']).one()
                newItem = Item(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category.id,
                               created_by=login_session['user_id'])
                session.add(newItem)
                session.commit()
                logger.info("Created new item.")
                flash('New Item %s Successfully Created' % (newItem.name))
                return redirect(url_for('showItems',
                                        category_name=category.name,
                                        login_session=login_session))
            else:
                return url_for(showLogin())
        else:
            return url_for(showLogin())

    else:
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories,
                               login_session=login_session)

###############################################################################


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    ''' Edit an item of a choosen category. '''
    editedItem = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(
        id=editedItem.category_id).one()
    if request.method == 'POST':
        if login_session:
            if login_session['username']:
                if editedItem.created_by != login_session['user_id']:
                    return "<script>function myFunction() {alert('You\
                            are not authorized to edit this item.\
                            Please create your own item in order\
                            to edit.');}</script><body onload='myFunction()'>"
                if request.form['name']:
                    editedItem.name = request.form['name']
                if request.form['description']:
                    editedItem.description = request.form['description']
                session.add(editedItem)
                session.commit()
                flash('Menu Item Successfully Edited')
                return redirect(url_for('showItems',
                                        category_name=category.name,
                                        login_session=login_session))
            else:
                return url_for(showLogin())
        else:
            return url_for(showLogin())

    else:
        return render_template('edititem.html',
                               category_name=category.name,
                               item=editedItem,
                               login_session=login_session)

###############################################################################


@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    ''' Delete an item of a choosen category.'''
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(
                                        id=itemToDelete.category_id).one()
    if login_session:
        if login_session['username']:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                flash('Item Successfully Deleted')
                return redirect(url_for('showItems',
                                        category_name=category.name,
                                        login_session=login_session))
            else:
                return render_template('deleteitem.html', item=itemToDelete,
                                       login_session=login_session)
        else:
            return url_for(showLogin())
    else:
        return url_for(showLogin())


###############################################################################
''' main code, running server on port 5000'''
###############################################################################


if __name__ == '__main__':

    # compatibilty for python 3
    try:
        xrange
    except NameError:
        xrange = range

    # Logger configuration
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # flask server
    app.secret_key = 'whiskas-sache'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
