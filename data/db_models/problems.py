import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Problem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    time_limit = sqlalchemy.Column(sqlalchemy.Float)
    memory_limit = sqlalchemy.Column(sqlalchemy.Integer)
    solves = sqlalchemy.Column(sqlalchemy.Integer)
