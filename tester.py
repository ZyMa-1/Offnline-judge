import datetime
import subprocess
import os
from time import sleep

from data.db_models import db_session
from data.db_models import users
from data.db_models import problems
from data.db_models.submissions import *

import schedule


def test_submission(submission, results):
    submission_path = f'data/testing_system/submissions/{submission.id}'
    problem_path = f'data/problems/{submission.problem_id}/tests'

    def delete_temp_files():
        os.remove(f'{submission_path}/submission.exe')
        os.remove(f'{submission_path}/input.txt')
        os.remove(f'{submission_path}/output.txt')

    os.rename(f'{submission_path}/{os.listdir(submission_path)[0]}', f'{submission_path}/submission.cpp')
    process = os.system(
        f"g++ -static -fno-strict-aliasing -DACMP -lm -s -x c++ -std=c++14 -Wl,--stack=67108864 -O2 -o {submission_path}/submission.exe {submission_path}/submission.cpp")
    if process != 0:
        results[submission.id] = {
            'status': 'CE',
            'running_time': 0
        }
        return
    test_num = 1
    max_running_time = 0
    for filename in os.listdir(f'{problem_path}/input'):
        input = open(f'{problem_path}/input/{filename}', 'r').read()
        output = open(f'{problem_path}/output/{filename}', 'r').read()

        open(f'{submission_path}/input.txt', 'w').write(input)
        start = datetime.now()
        subprocess.Popen(f"{submission_path}/submission.exe", stdin=open(f"{submission_path}/input.txt", "r"),
                         stdout=open(f"{submission_path}/output.txt", "w"))
        current_running_time = datetime.now() - start
        seconds = current_running_time.microseconds / 1000000
        max_running_time = max(max_running_time, seconds)
        sleep(.1)
        if max_running_time > submission.problem.time_limit:
            results[submission.id] = {
                'status': f"TLE {test_num}",
                'running_time': submission.problem.time_limit
            }
            return
        if open(f"{submission_path}/output.txt", "r").read() != output:
            delete_temp_files()
            results[submission.id] = {
                'status': f"WA {test_num}",
                'running_time': max_running_time
            }
            return
        test_num += 1
    delete_temp_files()
    results[submission.id] = {
        'running_time': max_running_time,
        'status': 'AC'
    }
    return


def test_all_submissions():
    res = {}
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.status == "In queue")
    for submission in submissions:
        test_submission(submission, res)
    for submission in submissions:
        submission.status = res[submission.id]['status']
        submission.running_time = res[submission.id]['running_time']
    session.commit()
    """
    processes = []
    for submission in submissions:
        p = multiprocessing.Process(target=test_submission, args=[submission, results])
        processes.append(p)
        p.start()

    for process in processes:
        process.join()
    for submission in submissions:
        submission.status = results[submission.id]['status']
        submission.running_time = results[submission.id]['running_time']
    session.commit()
    print(datetime.now() - start)
    print(results)
    """


def test_forever():
    db_session.global_init("data/db/main.sqlite")
    schedule.every(1).seconds.do(test_all_submissions)
    while 1:
        schedule.run_pending()