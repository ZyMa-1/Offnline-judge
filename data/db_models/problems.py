import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Problem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    solved_by = sqlalchemy.Column(sqlalchemy.Integer)
    time_limit = sqlalchemy.Column(sqlalchemy.Integer)
    memory_limit = sqlalchemy.Column(sqlalchemy.Integer)
