from db import DB_NAME, Base, User, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc

engine = create_engine('sqlite:///{}.db'.format(DB_NAME))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(name='Username', email='test@test.com', picture='/')
session.add(user)
session.commit()

categories = ['Music', 'Games', 'Videos']

items = ['Item_1', 'Item_2', 'Item_3']

cat_id = 1
for c in categories:
    category = Category(name=c)
    session.add(category)
    session.commit()

    for i in items:
        item = Item(name=i,description='Item Description',category_id=cat_id,user_id=1)
        session.add(item)
        session.commit()
    
    cat_id += 1

