import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

users_to_problems = sqlalchemy.Table('users_to_problems', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('users', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')),
                                     sqlalchemy.Column('problems', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('problems.id'))
                                     )


class Problem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    time_limit = sqlalchemy.Column(sqlalchemy.Float)
    memory_limit = sqlalchemy.Column(sqlalchemy.Integer)
    theme = sqlalchemy.Column(sqlalchemy.String)
