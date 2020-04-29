from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, session, abort, make_response, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import func as sqlalchemy_func
from wt_forms import *

from data.db_models import db_session

from data.db_models.submissions import *
from data.db_models.problems import *
from data.db_models.users import *

import os
from random import randint

from time import sleep

import multiprocessing

from tester import test_forever

app = Flask(__name__)
app.config['SECRET_KEY'] = 'This miss is pretty sad, but fuck it (C) WhiteCat'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def main():
    processes = []
    db_session.global_init("data/db/main.sqlite")
    p = multiprocessing.Process(target=test_forever)
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=app.run(port=8080))
    processes.append(p)
    p.start()
    for process in processes:
        process.join()


# Removing Cache
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = '0'
    response.headers["Pragma"] = "no-cache"
    return response


def remove_cache(page_url):
    response = make_response(url_for(page_url))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'


@app.route("/")
def start_page():
    return redirect('/home')


def base_params(title, navbar_active_tab_id):
    params = {
        "title": title,
        "navbar_active_tab_id": navbar_active_tab_id,
    }
    if current_user.is_authenticated:
        params["user_icon"] = url_for("static", filename=f"user_data/icons/{current_user.icon_id}.png")
    return params


@app.route("/home")
def home():
    params = base_params("Home page", 0)
    return render_template("home_page.html", **params)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    icon_folder_path = "static/user_data/icons"

    def resize_image(path):
        image = Image.open(path)
        image = image.resize((40, 40))
        image.save(path)

    def generate_icon_name():
        icon_id = randint(100000000, 999999999)
        icon_name = f"{icon_id}.png"
        while icon_name in os.listdir(icon_folder_path):
            icon_id = randint(100000000, 999999999)
            icon_name = f"{icon_id}.png"
        return icon_id, icon_name

    def save_custom_user_icon(icon_data):
        icon_id, icon_name = generate_icon_name()
        path = f"{icon_folder_path}/{icon_name}"
        open(path, 'wb').write(icon_data)
        resize_image(path)
        return icon_id

    def save_default_user_icon():
        num = randint(1, 3)  # 1-number of default icons
        icon_id, icon_name = generate_icon_name()
        path = f"{icon_folder_path}/{icon_name}"
        open(path, 'wb').write(open(f"data/default/user_icons/user_icon_{num}.png", "rb").read())
        resize_image(path)
        return icon_id

    form = SignUpForm()
    params = base_params("Sign up", -1)
    params["form"] = form
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            params["password_error_message"] = "Password mismatch"
            return render_template('sign_up.html', **params)
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            params["login_error_message"] = "This username already exists"
            return render_template('sign_up.html', **params)
        if session.query(User).filter(User.email == form.email.data).first():
            params["email_error_message"] = "This email already exists"
            return render_template('sign_up.html', **params)
        user = User(
            login=form.login.data,
            email=form.email.data,
        )
        icon_data = form.icon.data.read()
        if icon_data == b'':
            icon_id = save_default_user_icon()
        else:
            icon_id = save_custom_user_icon(icon_data)
        user.icon_id = icon_id
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/home')
    return render_template('sign_up.html', **params)


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    form = LogInForm()
    params = base_params("Log in", -1)
    params["form"] = form
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/home")
        params["error_message"] = "Wrong login or password"
        return render_template('log_in.html', **params)
    return render_template('log_in.html', **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/home")


@app.route('/practice', methods=['GET'])
def practice():
    params = base_params("Practice", 1)
    return render_template('practice.html', **params)


@app.route('/practice/basic_programming', methods=['GET'])
def basic_programming():
    session = db_session.create_session()
    params = base_params("Basic Programming", 1)
    params["problems"] = session.query(Problem).filter(Problem.theme == "basic_programming")
    if current_user.is_authenticated:
        params["problems_id"] = [problem.id for problem in current_user.problems_solved]
        params["try_problems_id"] = set([submission.problem.id for submission in current_user.submissions])
    else:
        params["problems_id"] = []
        params["try_problems_id"] = set()
    return render_template('basic_programming.html', **params)


@app.route('/practice/data_structures', methods=['GET'])
def data_structures():
    session = db_session.create_session()
    params = base_params("Data Structures", 1)
    params["problems"] = session.query(Problem).filter(Problem.theme == "data_structures")
    if current_user.is_authenticated:
        params["problems_id"] = [problem.id for problem in current_user.problems_solved]
        params["try_problems_id"] = set([submission.problem.id for submission in current_user.submissions])
    else:
        params["problems_id"] = []
        params["try_problems_id"] = set()
    return render_template('data_structures.html', **params)


@app.route('/practice/basic_programming/problems/<int:problem_id>', methods=['GET', 'POST'])
def basic_programming_problem(problem_id):
    session = db_session.create_session()
    form = SubmitForm()
    params = base_params("Fak me", 1)
    params["statement"] = f"problems/{problem_id}/statement.html"
    params["problem"] = session.query(Problem).filter(Problem.id == problem_id and Problem.theme == "basic_programming").first()
    params["title"] = params["problem"].title
    params["form"] = form
    params["goBack_href"] = "/practice/basic_programming"
    if form.validate_on_submit():
        code = request.form["code_area"]
        if code == "":
            params["message"] = "You can't submit empty code"
            return render_template('problem.html', **params)
        if not current_user.is_authenticated:
            params["message"] = "You must sign in to submit code"
            return render_template('problem.html', **params)
        submission_id = session.query(sqlalchemy_func.max(Submission.id)).one()[0] + 1
        submission_folder = f'data/testing_system/submissions/{submission_id}'
        os.mkdir(f'data/testing_system/submissions/{submission_id}')
        open(f"{submission_folder}/solution.cpp", "w").writelines([line.rstrip('\n') for line in code])
        submission = Submission(
            id=submission_id,
            user_id=current_user.id,
            problem_id=problem_id,
            status="In queue",
            running_time=0,
        )
        session.add(submission)
        session.commit()
        sleep(.5)
        return redirect(f'/practice/basic_programming/problems/{problem_id}/my_submissions')
    return render_template('problem.html', **params)


@app.route('/practice/basic_programming/problems/<int:problem_id>/my_submissions', methods=['GET'])
@login_required
def basic_programming_my_submissions(problem_id):
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.user_id == current_user.id).order_by(
        Submission.sending_time.desc())
    params = base_params("My submissions", 1)
    params["statement"] = f"problems/{problem_id}/statement.html"
    params["submissions"] = submissions
    params["problem"] = session.query(Problem).filter(Problem.id == problem_id).first()
    return render_template('my_submissions.html', **params)


@app.route('/practice/submissions/<int:submission_id>', methods=['GET'])
@login_required
def submission(submission_id):
    session = db_session.create_session()
    params = base_params("Submission", 1)
    params["code"] = open(f"data/testing_system/submissions/{submission_id}/submission.cpp", "r").read()
    params["submission"] = session.query(Submission).filter(Submission.id == submission_id).first()
    return render_template('submission.html', **params)


if __name__ == '__main__':
    main()
