import os
from flask import Flask, render_template, request, redirect, url_for, flash
# Anytime we run the python application a special variable named
#  __name__ is defined for the application in order to use it for
# all the imports
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

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
