from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, session, abort, make_response, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import func as sqlalchemy_func
from wt_forms import *

from data.db_models import db_session

from copy import copy

from data.db_models.submissions import *
from data.db_models.problems import *
from data.db_models.users import *

import os
from random import randint

from time import sleep

import multiprocessing

from tester import test_forever


def page_not_found_error(error):
    params = base_params("404 error", -1)
    return render_template('404.html', **params)


def unauthorized_error(error):
    params = base_params("401 error", -1)
    return render_template('401.html', **params)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'This miss is pretty sad, but fuck it (C) WhiteCat'
app.config["CACHE_TYPE"] = "null"

app.register_error_handler(404, page_not_found_error)
app.register_error_handler(401, unauthorized_error)

login_manager = LoginManager()
login_manager.init_app(app)

icon_folder_path = "static/user_data/icons"


def resize_image(path, w, h):
    image = Image.open(path)
    image = image.resize((w, h))
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
    path_small = f"{icon_folder_path}/small/{icon_name}"
    path_large = f"{icon_folder_path}/large/{icon_name}"
    open(path_small, 'wb').write(icon_data)
    open(path_large, 'wb').write(icon_data)
    resize_image(path_small, 40, 40)
    resize_image(path_large, 200, 200)
    return icon_id


def save_default_user_icon():
    num = randint(1, 3)  # 1-number of default icons
    icon_id, icon_name = generate_icon_name()
    path_small = f"{icon_folder_path}/small/{icon_name}"
    path_large = f"{icon_folder_path}/large/{icon_name}"
    icon_data = open(f"data/default/user_icons/user_icon_{num}.png", "rb").read()
    open(path_small, 'wb').write(icon_data)
    open(path_large, 'wb').write(icon_data)
    resize_image(path_small, 40, 40)
    resize_image(path_large, 200, 200)
    return icon_id


def delete_old_user_icon(icon_id):
    sleep(.05)
    os.remove(f"{icon_folder_path}/small/{icon_id}.png")
    os.remove(f"{icon_folder_path}/large/{icon_id}.png")


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


@app.route("/")
def start_page():
    return redirect('/home')


def base_params(title, navbar_active_tab_id):
    params = {
        "title": title,
        "navbar_active_tab_id": navbar_active_tab_id,
    }
    if current_user.is_authenticated:
        params["user_icon"] = url_for("static", filename=f"user_data/icons/small/{current_user.icon_id}.png")
        params["profile_url"] = f"/profile/{current_user.id}"
    return params


@app.route("/home")
def home():
    params = base_params("Home", 0)
    return render_template("home_page.html", **params)


@app.route("/introduction")
def introduction():
    params = base_params("Introduction", -1)
    return render_template("introduction.html", **params)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    session = db_session.create_session()

    form = SignUpForm()
    params = base_params("Sign up", -1)
    params["form"] = form
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            params["password_error_message"] = "Password mismatch"
            return render_template('sign_up.html', **params)
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


@app.route('/practice/<string:theme>', methods=['GET'])
def problem_list(theme):
    def theme_prettify():
        pretty_theme = theme.split('_')
        pretty_theme = ' '.join([it[0].upper() + it[1:].lower() for it in pretty_theme])
        return pretty_theme

    session = db_session.create_session()
    params = base_params(theme, 1)
    params["problems"] = session.query(Problem).filter(Problem.theme == theme)
    params["theme_title"] = theme_prettify()
    if current_user.is_authenticated:
        params["problems_solved_id"] = [problem.id for problem in current_user.problems_solved]
        params["problems_unsolved_id"] = [problem.id for problem in current_user.problems_unsolved]
    else:
        params["problems_solved_id"] = []
        params["problems_unsolved_id"] = set()
    return render_template('problems_list.html', **params)


@app.route('/practice/<string:theme>/problems/<int:problem_id>', methods=['GET', 'POST'])
def problem(theme, problem_id):
    session = db_session.create_session()
    form = SubmitForm()
    params = base_params("Fak me", 1)
    params["statement"] = f"problems/{problem_id}/statement.html"
    params["problem"] = session.query(Problem).filter(Problem.id == problem_id, Problem.theme == theme).first()
    params["title"] = params["problem"].title
    params["form"] = form
    params["goBack_href"] = f"/practice/{params['problem'].theme}"
    params["active_tab_id"] = 0
    if form.validate_on_submit():
        code = request.form["code_area"]
        if code == "":
            params["message"] = "You can't submit empty code"
            return render_template('problem.html', **params)
        if not current_user.is_authenticated:
            params["message"] = "You must sign in to submit code"
            return render_template('problem.html', **params)
        submission_id = 1
        if session.query(Submission).first():
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
        return redirect(f'/practice/{theme}/problems/{problem_id}/my_submissions')
    return render_template('problem.html', **params)


@app.route('/practice/<string:theme>/problems/<int:problem_id>/my_submissions', methods=['GET'])
@login_required
def my_submissions_on_problem(theme, problem_id):
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.user_id == current_user.id).order_by(
        Submission.sending_time.desc())
    submissions = list(filter(lambda it: it.problem.theme == theme, submissions))
    params = base_params("My submissions", 1)
    params["statement"] = f"problems/{problem_id}/statement.html"
    params["submissions"] = submissions
    params["problem"] = session.query(Problem).get(problem_id)
    params["active_tab_id"] = 2
    return render_template('my_submissions_on_problem.html', **params)


@app.route('/practice/submissions/<int:submission_id>', methods=['GET'])
@login_required
def submission(submission_id):
    session = db_session.create_session()
    params = base_params("Submission", 1)
    params["code"] = open(f"data/testing_system/submissions/{submission_id}/submission.cpp", "r").read()
    params["submission"] = session.query(Submission).get(submission_id)
    return render_template('submission.html', **params)


@app.route('/practice/<string:theme>/problems/<int:problem_id>/editorial', methods=['GET'])
def editorial(theme, problem_id):
    session = db_session.create_session()
    params = base_params("Editorial", 1)
    params["editorial"] = f"problems/{problem_id}/editorial.html"
    params["active_tab_id"] = 1
    params["code"] = open(f"templates/problems/{problem_id}/author_solution.cpp", "r").read()
    params["problem"] = session.query(Problem).get(problem_id)
    return render_template('editorial.html', **params)


@app.route('/submissions', methods=['GET'])
def submissions():
    session = db_session.create_session()
    params = base_params("Submissions", 2)
    params["submissions"] = session.query(Submission).order_by(Submission.id.desc()).limit(20).all()
    return render_template('submissions.html', **params)


@app.route('/my_submissions', methods=['GET'])
@login_required
def my_submissions():
    session = db_session.create_session()
    submissions = session.query(Submission).filter(Submission.user_id == current_user.id).order_by(
        Submission.sending_time.desc())
    params = base_params("My submissions", -1)
    params["submissions"] = submissions
    return render_template('my_submissions.html', **params)


@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    session = db_session.create_session()

    def parse_user_statistics(user):
        submissions_results = {
            "AC": 0,
            "WA": 0,
            "TLE": 0,
            "MLE": 0,
            "CE": 0,
            "RE": 0
        }
        ans_dict = {
            "AC": 0,
            "WA": 0,
            "TLE": 0,
            "MLE": 0,
            "CE": 0,
            "RE": 0,
            "accuracy": 0,
            "problems_solved": 0,
            "languages": ["C++11"],
            "skills": ["soon..."]
        }
        submissions_num = 0
        for submission in user.submissions:
            for key in submissions_results.keys():
                if key in submission.status:
                    ans_dict[key] += 1
                    break
            submissions_num += 1
        if submissions_num == 0:
            ans_dict["accuracy"] = 100
            return ans_dict
        ans_dict["accuracy"] = int(round(len(user.problems_solved) / submissions_num, 2) * 100)
        return ans_dict

    params = base_params("Profile", -1)
    params["user"] = session.query(User).get(user_id)
    params["user_statistics"] = parse_user_statistics(params["user"])
    params["profile_icon"] = f"/static/user_data/icons/large/{params['user'].icon_id}.png"
    params["table_headers"] = ["AC", "CE", "WA", "TLE", "MLE", "RE"]

    return render_template('profile.html', **params)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    d_session = db_session.create_session()
    user = d_session.query(User).get(current_user.id)
    params = base_params("Profile edit", -1)
    if "error_parameters" in session.keys():
        for key in session["error_parameters"]:
            params[key] = session["error_parameters"][key]
        session.pop("error_parameters", None)
    params["profile_icon"] = f"/static/user_data/icons/large/{user.icon_id}.png"
    params["user_icon"] = f"/static/user_data/icons/small/{user.icon_id}.png"

    req_ans = str(request.form)
    is_email_form, is_icon_form, is_password_form = 0, 0, 0
    if "email" in req_ans:
        params["email_change_form_visible_errors"] = True
        is_email_form = 1
    elif "password" in req_ans:
        params["password_change_form_visible_errors"] = True
        is_password_form = 1
    elif "Change icon" in req_ans:
        params["icon_change_form_visible_errors"] = True
        is_icon_form = 1
    icon_change_form = IconChangeForm()
    email_change_form = EmailChangeForm()
    password_change_form = PasswordChangeForm()
    params["icon_change_form"] = icon_change_form
    params["email_change_form"] = email_change_form
    params["password_change_form"] = password_change_form
    if icon_change_form.validate_on_submit():  # can put one of 3 form, because they all validating(important line)
        if is_email_form:
            if d_session.query(User).filter(User.email == email_change_form.email.data).first():
                params["email_error_message"] = "This email already linked to another user"
            else:
                user.email = email_change_form.email.data
        if is_icon_form:
            delete_old_user_icon(user.icon_id)
            sleep(.05)
            icon_data = icon_change_form.icon.data.read()
            if icon_data == b'':
                icon_id = save_default_user_icon()
            else:
                icon_id = save_custom_user_icon(icon_data)
            user.icon_id = icon_id
        if is_password_form:
            if password_change_form.new_password.data != password_change_form.new_password_repeat.data:
                params["password_error_message"] = "Password mismatch"
            elif not user.check_password(password_change_form.old_password.data):
                params["password_error_message"] = "Wrong old password"
            else:
                user.set_password(password_change_form.new_password.data)
        d_session.commit()
        error_params = {}
        if "email_error_message" in params.keys():
            error_params["email_error_message"] = params["email_error_message"]
        if "password_error_message" in params.keys():
            error_params["password_error_message"] = params["password_error_message"]
        session["error_parameters"] = error_params
        return redirect(url_for('profile_edit'))
    return render_template('edit_profile.html', **params)


if __name__ == '__main__':
    main()
