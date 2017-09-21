from flask import Flask
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
	output = ''
	menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	output += restaurant.name + '</br>' + '</br>'
	for i in menuItems:
		output += '&nbsp' + '&nbsp' + '&nbsp'
		output += i.name
		output += '</br>'
		output += '&nbsp' + '&nbsp' + '&nbsp'
		output += i.description
		output += '</br>'
		output += '&nbsp' + '&nbsp' + '&nbsp'
		output += i.price
		output += '</br>' + '</br>'
	return output

# Method to add new restaurant menu item
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/new')
def addNewMenuItem(restaurant_id):
	return "page to create a new menu item"

# Method to edit restaurant menu item using item id
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/edit')
def editMenuItem(restaurant_id, item_id):
	return "page to edit a menu item"

# Method to delete restaurant menu item using item id
# for one restaurant by using restaurant id
@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/delete')
def deleteMenuItem(restaurant_id, item_id):
	return "page to delete a menu item"

# The python file ran by python interpreter gets the by default name __main__
# While for all other imported python files, __name__ variable is set to
# actual python file name
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
