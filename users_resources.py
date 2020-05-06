from flask import jsonify
from flask_restful import abort, Resource

from data.db_models import db_session
from data.db_models.users import *


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User with id {user_id} not found")


def parse_user(user):
    ans_dict = user.to_dict(only=('id', 'login', 'email', 'icon_id'))
    problems_solved_id = []
    for problem in user.problems_solved:
        problems_solved_id.append(problem.id)
    ans_dict["problems_solved"] = problems_solved_id
    problems_unsolved_id = []
    for problem in user.problems_unsolved:
        problems_unsolved_id.append(problem.id)
    ans_dict["problems_unsolved"] = problems_unsolved_id
    submissions_id = []
    for submission in user.submissions:
        submissions_id.append(submission.id)
    ans_dict["submissions"] = submissions_id
    return ans_dict


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': parse_user(user)})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        users_dict_list = []
        for user in users:
            users_dict_list.append(parse_user(user))
        return jsonify({'users': users_dict_list})
