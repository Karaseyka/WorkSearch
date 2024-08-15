import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase
from data.models.user import User


class Parent(User, UserMixin, SerializerMixin):
    __tablename__ = 'parent'
    id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id"), primary_key=True)
    child \
        = sqlalchemy.Column(sqlalchemy.String)
    otkliks = sqlalchemy.Column(sqlalchemy.String)
    __mapper_args__ = {
        'with_polymorphic': '*',
        "polymorphic_identity": "parent"
    }
