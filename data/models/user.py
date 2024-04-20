import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    contacts = sqlalchemy.Column(sqlalchemy.String)
    role = sqlalchemy.Column(sqlalchemy.String)
    resume = sqlalchemy.Column(sqlalchemy.BLOB, default=None)
    resumetxt = sqlalchemy.Column(sqlalchemy.String)
    child \
        = sqlalchemy.Column(sqlalchemy.String)
    works = sqlalchemy.Column(sqlalchemy.String)
    parent = sqlalchemy.Column(sqlalchemy.Integer)
    parentreq = sqlalchemy.Column(sqlalchemy.Integer)
    parent = sqlalchemy.Column(sqlalchemy.Integer)
    parentreq = sqlalchemy.Column(sqlalchemy.Integer)
    otkliks = sqlalchemy.Column(sqlalchemy.String)
    worksfromparent = sqlalchemy.Column(sqlalchemy.String)
