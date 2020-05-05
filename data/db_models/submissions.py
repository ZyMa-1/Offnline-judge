from datetime import datetime

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Submission(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'submissions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    problem_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("problems.id"))
    status = sqlalchemy.Column(sqlalchemy.String)
    running_time = sqlalchemy.Column(sqlalchemy.Integer)  # in ms
    sending_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    user = orm.relation("User")
    problem = orm.relation("Problem")
