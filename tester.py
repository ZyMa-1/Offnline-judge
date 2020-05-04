import datetime
import subprocess
import os
from time import sleep

import psutil

from data.db_models import db_session
from data.db_models import users
from data.db_models import problems
from data.db_models.problems import Problem
from data.db_models.submissions import *

from data.db_models.users import User


def test_submission(submission, results):
    submission_path = f'data/testing_system/submissions/{submission.id}'
    problem_path = f'data/problems/{submission.problem_id}/tests'

    def delete_temp_files():
        sleep(1)
        try:
            os.remove(f'{submission_path}/submission.exe')
        except Exception:
            pass
        try:
            os.remove(f'{submission_path}/input.txt')
        except Exception:
            pass
        try:
            os.remove(f'{submission_path}/output.txt')
        except Exception:
            pass
        try:
            os.remove(f'{submission_path}/err.txt')
        except Exception:
            pass

    err_file_path = f'{submission_path}/err.txt'
    os.rename(f'{submission_path}/{os.listdir(submission_path)[0]}', f'{submission_path}/submission.cpp')
    try:
        subprocess.check_call(
            f"g++ -static -std=c++11 -o {submission_path}/submission.exe {submission_path}/submission.cpp",
            stderr=open(err_file_path, 'w'))
    except subprocess.CalledProcessError:
        error = open(err_file_path, 'r').read()
        if "does not name a type" in error or "undefined" in error:
            results[submission.id] = {
                'status': 'CE',
                'running_time': 0
            }
        else:
            results[submission.id] = {
                'status': 'MLE 1',
                'running_time': 0
            }
        return delete_temp_files()
    test_num = 1
    max_running_time = 0
    for filename in os.listdir(f'{problem_path}/input'):
        input = open(f'{problem_path}/input/{filename}', 'r').read()
        output = open(f'{problem_path}/output/{filename}', 'r').read()

        open(f'{submission_path}/input.txt', 'w').write(input)
        start = datetime.now()
        try:
            subprocess.check_call(
                f"{submission_path}/submission.exe",
                stdin=open(f"{submission_path}/input.txt", "r"),
                stdout=open(f"{submission_path}/output.txt", "w"),
                timeout=submission.problem.time_limit)
            current_running_time = datetime.now() - start
        except subprocess.TimeoutExpired:
            sleep(.5)
            results[submission.id] = {
                'status': f"TLE {test_num}",
                'running_time': submission.problem.time_limit
            }
            return delete_temp_files()
        sleep(.1)
        if -1 > submission.problem.memory_limit:
            results[submission.id] = {
                'status': f"MLE {test_num}",
                'running_time': max_running_time
            }
            return delete_temp_files()
        seconds = current_running_time.microseconds / 1000000
        if test_num == 1:
            seconds -= 0.1
        max_running_time = max(max_running_time, seconds)
        sleep(.5)
        submission_output = open(f"{submission_path}/output.txt", "r").read()
        submission_output = submission_output.strip('\n').strip(' ').rstrip('\n').rstrip(' ')  # delete extra \n
        if submission_output != output:
            results[submission.id] = {
                'status': f"WA {test_num}",
                'running_time': max_running_time
            }
            return delete_temp_files()
        test_num += 1
    results[submission.id] = {
        'running_time': max_running_time,
        'status': 'AC'
    }
    return delete_temp_files()


def test_all_submissions():
    res = {}
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.status == "In queue")
    for submission in submissions:
        test_submission(submission, res)
        submission.status = res[submission.id]['status']
        submission.running_time = res[submission.id]['running_time']
        if submission.status == "AC":
            if submission.problem in submission.user.problems_unsolved:
                submission.user.problems_unsolved.remove(submission.problem)
            if submission.problem not in submission.user.problems_solved:
                submission.user.problems_solved.append(submission.problem)
        else:
            if submission.problem not in submission.user.problems_unsolved:
                submission.user.problems_unsolved.append(submission.problem)
        session.commit()


def test_forever():
    db_session.global_init("data/db/main.sqlite")
    while 1:
        test_all_submissions()
        sleep(1)
