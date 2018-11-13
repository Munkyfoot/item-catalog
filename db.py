"""The model for the Item Catalog web app."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

DB_NAME = 'catalog'


class User(Base):
    """Define User table for SQLAlchemy."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    picture = Column(String(150), nullable=False)


class Category(Base):
    """Define Category table for SQLAlchemy."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):
    """Define Item table for SQLAlchemy."""

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=False)
    image_url = Column(String(300), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///{}.db'.format(DB_NAME))


Base.metadata.create_all(engine)
