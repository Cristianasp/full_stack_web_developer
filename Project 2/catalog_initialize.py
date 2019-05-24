#!/usr/bin/env python
'''
Udacity Nanodegree FullStack Web developer
Project  Item Catalog
Author: Cristiana Parada 
Database initialization:
    create user system
    insert categories
'''

###############################################################################


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime

from catalog_database import User, Category, Item

engine = create_engine('sqlite:///Catalog.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

###############################################################################
# Create user system
###############################################################################


user_sys = User(
    username="System",
    email="cris@best.com.br",
    origin="Internal",
    password_hash="SecretPassword123!@#")
session.add(user_sys)
session.add
session.commit()
user = session.query(User).filter_by(email="cris@best.com.br").one()

###############################################################################
# Create 7 categories and log it
###############################################################################


for cat in ["Soccer", "BasketBall", "Baseball", "Frisbee", "Snowboarding",
            "Rock Climbing", "Foosball", "Skating", "Hockey"]:
    categoryN = Category(name=cat)
    session.add(categoryN)
    session.commit()

###############################################################################
# Create some items and log it
###############################################################################


itemN = Item(name="Professional Disc",
             description="Professional rounded disk for outdoor activities",
             category_id=4,
             created_by = user.id)
session.add(itemN)
session.commit()

itemN = Item(name="Snowboard",
             description=" Snowboard is a big surf idea, it makes you happy",
             category_id=5,
             created_by = user.id)
session.add(itemN)
session.commit()

'''
Right now there is a lot code repetition in order to add your test data,
which increases the chance of an error while writing to your DB.
It's also not very convenient to do for many DB items, even if you wanted to
randomly generate test data or fetch it from online data.
Python comes with powerful packages/module like json, csv.

Why not store your test data in a suitable data model, such as a JSON, and
iterate through it with a method.
the great advantage of doing it this way, is that the code that actually
touches your DB is only written once, you could easily write random test data
to fill it to make it as large as you need with no extra work, or you can fill
it with sample data from online sites. You could of course also export and
import it via a JSON file.

An example code (with different database schema):

category_json = json.loads("""{
"all_categories": [
  {
    "created_date": null,
    "id": 29,
    "name": "Books",
    "no_of_visits": 1
  },
  {
    "created_date": null,
    "id": 21,
    "name": "Camping",
    "no_of_visits": 7
  },
  {
    "created_date": null,
    "id": 20,
    "name": "Kitchenware",
    "no_of_visits": 1
  },
  {
    "created_date": null,
    "id": 32,
    "name": "Laptops",
    "no_of_visits": 10
  },

  {
    "created_date": null,
    "id": 31,
    "name": "Susan's Moving Items",
    "no_of_visits": 8
  }
]
}""")

for e in category_json['all_categories']:
category_input = Category(
  name=str(e['name']),
  id=str(e['id']),
  no_of_visits=0,
  user_id=1
  )
session.add(category_input)
session.commit()
'''
###############################################################################
# Finished
###############################################################################


print("Finished ! Added categories and user system !")
