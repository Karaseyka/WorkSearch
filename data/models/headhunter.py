import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase
from data.models.user import User


class Headhunter(User, UserMixin, SerializerMixin):
    __tablename__ = 'headhunter'
    id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id"), primary_key=True)
    contacts = sqlalchemy.Column(sqlalchemy.String)
    works = sqlalchemy.Column(sqlalchemy.String)
    otkliks = sqlalchemy.Column(sqlalchemy.String)
    __mapper_args__ = {
        'with_polymorphic': '*',
        'polymorphic_identity': 'headhunter'
    }

