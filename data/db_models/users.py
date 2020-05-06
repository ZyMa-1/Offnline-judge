import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    icon_id = sqlalchemy.Column(sqlalchemy.String)  # relative path to icon
    submissions = orm.relation("Submission", back_populates='user')  # list of submissions(one-to-many)
    problems_solved = orm.relation("Problem",
                                   secondary="users_to_solved_problems",
                                   backref="users_solved", lazy='subquery')  # many-to-many
    problems_unsolved = orm.relation("Problem",
                                     secondary="users_to_unsolved_problems",
                                     backref="users_unsolved", lazy='subquery')  # many-to-many

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
