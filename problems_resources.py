from flask import jsonify
from flask_restful import abort, Resource

from data.db_models import db_session
from data.db_models.problems import *


def abort_if_problem_not_found(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404, message=f"Problem with id {problem_id} not found")


def parse_problem(problem):
    ans_dict = problem.to_dict(only=('id', 'title', 'time_limit', 'memory_limit', 'theme'))
    return ans_dict


class ProblemResource(Resource):
    def get(self, problem_id):
        abort_if_problem_not_found(problem_id)
        session = db_session.create_session()
        problem = session.query(Problem).get(problem_id)
        return jsonify({'problem': parse_problem(problem)})


class ProblemsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        problems = session.query(Problem).all()
        problems_dict_list = []
        for problem in problems:
            problems_dict_list.append(parse_problem(problem))
        return jsonify({'problems': problems_dict_list})
