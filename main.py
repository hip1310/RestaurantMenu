import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Imports for adding anti-forgery state token
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Anytime we run the python application a special variable named
#  __name__ is defined for the application in order to use it for
# all the imports
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Create a state token to prevent request forgery
# Store it in a session for later validation
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_letters + string.digits)
		            for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

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

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Method to view restaurant menu for one restaurant by using restaurant id
# @ specifies decorator that wraps the viewRestaurantMenu() function inside
# the app.route() function so that viewRestaurantMenu() gets called
# whenever the specified routes are sent from the browser
@app.route('/restaurant/<int:restaurant_id>')
def viewRestaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)

	# jinja2 template engine provides HTML escaping
	# Flask will look for templates sepcified in render_template method into
	# /templates folder
	# Here the query results for restaurant and menuItems are passed to
	# the menu.html template
	return render_template('menu.html', restaurant=restaurant, 
		                                menuItems=menuItems)

# Method to add new restaurant menu item
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/new', methods=['GET','POST'])
def addNewMenuItem(restaurant_id):
	# When 'GET' request is received, We will display the html page
	# to add new menu item.
	if request.method == 'GET':
		return render_template('newMenuItem.html', restaurant_id
			                                      =restaurant_id)
	# When 'POST' request is received, We will use database session
	# to insert new data in menuitem table and then using Flask's
	# redirect feature, redirect to the page to view all menu items
	# for that restaurant.
	elif request.method == 'POST':
		newMenuItem = MenuItem(name=request.form['name'],
					  description=request.form['description'],
                      price=request.form['price'], restaurant_id=restaurant_id)
		session.add(newMenuItem)
		session.commit()
		# store a flash message in session
		# We will use this message to give feedback to user in html page.
		flash("Successfully added new menu item!!!")
		return redirect(url_for('viewRestaurantMenu', restaurant_id=
			                    restaurant_id))

# Method to edit restaurant menu item using item id
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/edit',
	                                     methods=['GET','POST'])
def editMenuItem(restaurant_id, item_id):
	menuItem = session.query(MenuItem).filter_by(id=item_id).one()
	# When 'GET' request is received, We will display the html page
	# to edit menu item.
	if request.method == 'GET':
		return render_template('editMenuItem.html', restaurant_id
			                    =restaurant_id, item=menuItem)
	# When 'POST' request is received, We will use database session
	# to update data in menuitem table and then using Flask's
	# redirect feature, redirect to the page to view all menu items
	# for that restaurant.
	elif request.method == 'POST':
		if request.form['name']:
			menuItem.name = request.form['name']
		if request.form['description']:
			menuItem.description = request.form['description']
		if request.form['price']:
			menuItem.price = request.form['price']
		session.add(menuItem)
		session.commit()
		flash("Successfully edited menu item!!!")
		return redirect(url_for('viewRestaurantMenu', restaurant_id=
			                    restaurant_id))

# Method to delete restaurant menu item using item id
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/delete',
											methods=['GET','POST'])
def deleteMenuItem(restaurant_id, item_id):
	menuItem = session.query(MenuItem).filter_by(id=item_id).one()
	# When 'GET' request is received, We will display the html page
	# to delete menu item.
	if request.method == 'GET':
		return render_template('deleteMenuItem.html', restaurant_id
			                    =restaurant_id, item=menuItem)
	# When 'POST' request is received, We will use database session
	# to delete item record in menuitem table and then using Flask's
	# redirect feature, redirect to the page to view all menu items
	# for that restaurant.
	elif request.method == 'POST':
		session.delete(menuItem)
		session.commit()
		flash("Successfully deleted menu item!!!")
		return redirect(url_for('viewRestaurantMenu', restaurant_id=
			                    restaurant_id))

# API to get all the menuitems of a restaurant in json format
# Flask's jsonify() funcion turns the JSON output into a Response object
# with the application/json mimetype.
@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenuAsJson(restaurant_id):
	items = session.query(MenuItem).filter_by(restaurant_id
		                                      =restaurant_id).all()
	return jsonify(MenuItems = [i.serialize for i in items])

# API to get a single menu item of a restaurant in json format
@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>')
def menuItemAsJson(restaurant_id, item_id):
	item = session.query(MenuItem).filter_by(id=item_id).one()
	return jsonify(MenuItem = [item.serialize])

# The python file ran by python interpreter gets the by default name __main__
# While for all other imported python files, __name__ variable is set to
# actual python file name
if __name__ == '__main__':
	"""
	session object in flask allows to store information specific to a user
	from one request to the next (or from one web page to another.)
	In order to use sessions we have to set a secret key.
	Message flashing in Flask works using a session.
	"""
	app.secret_key = os.urandom(24)
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
