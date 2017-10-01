#### Configuration at the start of the file ####
#### Sets up all the dependencies needed for database ####
#### Binds the code to SQLAlchemy engine ####
# Create instance of declarative base class in order to inherit all the features of the SQLAlchemy #

# Needed to manipulate different parts of python run-time environment
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

# Needed to create foreign key relationship
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# Create instance of the declarative_base class #
# declarative_base would let sqlalchemy know that our classes are
# special sqlalchemy classes that corresponds to the tables in our database #
Base = declarative_base()

# Representation of a restaurant table as a python class
# Python class used to represent the table extends the Base class
class Restaurant(Base):
    __tablename__ = 'restaurant'

    # Map python objects to columns in our database
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

# Representation of a menu_item table as a python class
class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    # Function to send JSON objects in a serializable format
    @property
    def serialize(self):
        return{
            'id'          : self.id,
            'name'        : self.name,
            'description' : self.description,
            'price'       : self.price,
            'course'      : self.course
        }

#### Configuration at the end of the file ####
# Create (or connect) the database and add tables and columns #
# Create the database file
engine = create_engine('sqlite:///restaurantmenu.db')

# Adds tables into the database from the classes we create here
Base.metadata.create_all(engine)