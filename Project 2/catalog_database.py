#!/usr/bin/env python
'''
Udacity Nanodegree FullStack Web developer
Project  Item Catalog
Author: Cristiana Parada 
Database creation and related classes
'''

###############################################################################


from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

###############################################################################


class User(Base):
    ''' Table user has the information about the users.

    In order to acess the item catalog, the user should have an account with
    facebook or google.
    The source of authentication will be stored, as long as username, email
    picture, hash
    '''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    email = Column(String(32), index=True)
    origin = Column(String(32))
    picture = Column(String(250))
    password_hash = Column(String(64))
    provider = Column(String(32))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

###############################################################################


class Category(Base):
    ''' Table Category refers to the possible categories of the Catalog'''
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }

###############################################################################


class Item(Base):
    ''' Table Item refers to an item in the catalog. '''
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    created_by = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description}
            ''' Great work serializing object data, you just need to serialize
            category_id and created_by as well.
            '''
###############################################################################
# Run this once, to create the database
###############################################################################
if __name__ == '__main__':
    engine = create_engine('sqlite:///Catalog.db')
    Base.metadata.create_all(engine)

###############################################################################
