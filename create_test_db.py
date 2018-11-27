#!/usr/bin/env python
"""Generate a complete database for testing the Item Catalog web app."""

from db import DB_USER, DB_PASS, DB_NAME, Base, User, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc

engine = create_engine('postgresql://{}:{}@localhost/{}'.format(
    DB_USER, DB_PASS, DB_NAME))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(name='Username', email='user@test.com')
session.add(user)
session.commit()

categories = ['Category_1', 'Category_2', 'Category_3']

items = ['Item_1', 'Item_2', 'Item_3']

cat_id = 1
for c in categories:
    category = Category(name=c)
    session.add(category)
    session.commit()

    for i in items:
        item = Item(name=i, description='Item Description',
                    category_id=cat_id, user_id=1)
        session.add(item)
        session.commit()

    cat_id += 1
