from flask import jsonify
from flask_restful import abort, Resource

from data.db_models import db_session
from data.db_models.submissions import *


def abort_if_submission_not_found(submission_id):
    session = db_session.create_session()
    user = session.query(Submission).get(submission_id)
    if not user:
        abort(404, message=f"Submission with id {submission_id} not found")


def parse_submission(submission):
    ans_dict = submission.to_dict(only=('id', 'user_id', 'problem_id', 'status', 'running_time', 'sending_time'))
    return ans_dict


class SubmissionResource(Resource):
    def get(self, submission_id):
        abort_if_submission_not_found(submission_id)
        session = db_session.create_session()
        user = session.query(Submission).get(submission_id)
        return jsonify({'submission': parse_submission(user)})


class SubmissionsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        submissions = session.query(Submission).all()
        submissions_dict_list = []
        for submission in submissions:
            submissions_dict_list.append(parse_submission(submission))
        return jsonify({'submissions': submissions_dict_list})
