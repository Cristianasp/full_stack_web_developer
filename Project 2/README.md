# Catalog APP

This is a catalog project that stores and shows catalog information.

The catalog has categories and items.

Each category has a name and a description.

Each item has a name, a description and is related to a category.

## Requirements

To run this catalog, the following software and libraries are necessary:

* PostgreSQL - installation instructions [here](https://www.postgresql.org/docs/9.3/installation.html)
* Python 2.7 - installation instructions [here](https://www.python.org/downloads/)
* Additional Python libraries:
    * flask - installation instructions [here](http://flask.pocoo.org/docs/1.0/installation/)
    * oauth2client.client - installation instructions [here](https://oauth2client.readthedocs.io/en/latest/)
    * requests - installation instructions [here](https://2.python-requests.org//en/v2.7.0/user/install/)
    * sqlalchemy - installation instructions [here](https://pypi.org/project/SQLAlchemy/)

**Important information** : In order to authenticate using Facebook and Google authentication, the secret keys for Google and Facebook are not provided with the code. Valid client IDs are not provided in login.html. 

## How to run this project

A database is necessary to run this project.

To create the database, run:

```sh
$ python catalog_database.py
```
To create some initial data in the database, run:

```sh
$ python catalog_initialize.py
```

To start the server, run:

```sh
$ python application.py
```

To access the application, open a browser and type:

http://localhost:8000


## Catalog functionalities

### Json catalog

Go to [this page](http://localhost:8000/catalog.json) to see a json list of all items in the catalog.

### List Categories

Go to [this page](http://localhost:8000/) to see all categories and the most recent added items.

### List items of a given category

From the initial category page, select the desired category and it will show all items of that category.

### Create new items

You can create new items related to the existing categories.

### Edit items

You can change name and description of a given item.

### Delete items

You can delete an item.

### Facebook and Google authentication

It is possible to login in the application using Google or Facebook authentication.

#### Author

Cristiana Parada
