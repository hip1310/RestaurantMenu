from flask import Flask
# Anytime we run the python application a special variable named
#  __name__ is defined for the application in order to use it for
# all the imports
app = Flask(__name__)

# decorator that wraps the HelloWorld() function inside
# the app.route() function so that HelloWorld() gets called
# whenever the specified routes are sent from the browser
@app.route('/')
@app.route('/hello')
def HelloWorld():
	return "Hello World"

# The python file ran by python interpreter gets the by default name __main__
# While for all other imported python files, __name__ variable is set to
# actual python file name
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
