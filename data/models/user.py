import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, case
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    role = sqlalchemy.Column(sqlalchemy.String)

    __mapper_args__ = {
        'with_polymorphic': '*',

        'polymorphic_on': case(
            (role == "option1", "child"),
            (role == "option2", "parent"),
            (role == "option3", "headhunter"),
            else_="user"),
        'polymorphic_identity': 'user'
    }
