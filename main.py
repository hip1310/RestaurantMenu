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

# decorator that wraps the HelloWorld() function inside
# the app.route() function so that HelloWorld() gets called
# whenever the specified routes are sent from the browser
@app.route('/menuitems')
def getMenuItems():
	restaurants = session.query(Restaurant).all()
	output = ''
	for j in restaurants:	
		menuItems = session.query(MenuItem).filter_by(restaurant_id = j.id)
		output += j.name + '</br>' + '</br>'
		for i in menuItems:
			output += '&nbsp' + '&nbsp' + '&nbsp'
			output += i.name
			output += '</br>' + '</br>'
        return output

# The python file ran by python interpreter gets the by default name __main__
# While for all other imported python files, __name__ variable is set to
# actual python file name
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
