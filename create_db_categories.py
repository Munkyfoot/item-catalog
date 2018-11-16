#!/usr/bin/env python
"""Generate a database with give categories for the Item Catalog web app."""

from db import DB_NAME, Base, User, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc

engine = create_engine('sqlite:///{}.db'.format(DB_NAME))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

categories = ['Music', 'Film', 'Games']

for c in categories:
    category = Category(name=c)
    session.add(category)
    session.commit()
