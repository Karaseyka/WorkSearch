import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase


class Vacancy(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'vacancies'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    salary = sqlalchemy.Column(sqlalchemy.String)
    minimal_age = sqlalchemy.Column(sqlalchemy.String)

