import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin

from data.database.db_session import SqlAlchemyBase
from data.models.user import User


class Child(User, UserMixin, SerializerMixin):
    __tablename__ = 'child'
    id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id"), primary_key=True)
    resume = sqlalchemy.Column(sqlalchemy.BLOB, default=None)
    resumetxt = sqlalchemy.Column(sqlalchemy.String)
    parent = sqlalchemy.Column(sqlalchemy.Integer)
    parentreq = sqlalchemy.Column(sqlalchemy.Integer)
    otkliks = sqlalchemy.Column(sqlalchemy.String)
    worksfromparent = sqlalchemy.Column(sqlalchemy.String)
    __mapper_args__ = {
        'with_polymorphic': '*',
        'polymorphic_identity': 'child'
    }
