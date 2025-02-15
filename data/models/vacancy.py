import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase


class Vacancy(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'vacancies'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id")) # id работодателя
    name = sqlalchemy.Column(sqlalchemy.String) # название вакансии
    description = sqlalchemy.Column(sqlalchemy.String) # описание вакансии
    minimal_age = sqlalchemy.Column(sqlalchemy.String) # минимальный возраст на отклик
    salary = sqlalchemy.Column(sqlalchemy.Integer) # зарплата
    town = sqlalchemy.Column(sqlalchemy.String) # город
    address = sqlalchemy.Column(sqlalchemy.String) # полный адрес

