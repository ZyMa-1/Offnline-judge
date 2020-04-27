from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, session, abort, make_response, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from wt_forms import *

from data.db_models import db_session

from data.db_models.submissions import *
from data.db_models.problems import *
from data.db_models.users import *

import os
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'This miss is pretty sad, but fuck it (C) WhiteCat'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def main():
    db_session.global_init("data/db/main.sqlite")
    app.run(port=8080)


# Removing Cache
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = '0'
    response.headers["Pragma"] = "no-cache"
    return response


def remove_cache():
    response = make_response(url_for('sign_up'))
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


@app.route('/practice', methods=['GET', 'POST'])
def practice():
    params = base_params("Practice", 1)
    return render_template('practice.html', **params)


@app.route('/practice/basic_programming', methods=['GET', 'POST'])
def basic_programming():
    session = db_session.create_session()
    params = base_params("Basic Programming", 1)
    params["problems"] = session.query(Problem).all()
    return render_template('basic_programming.html', **params)


@app.route('/practice/basic_programming/problems/<int:problem_id>', methods=['GET', 'POST'])
def basic_programming_problem(problem_id):
    session = db_session.create_session()
    form = SubmitForm()
    params = base_params("Basic Programming", 1)
    params["statement"] = f"problems/{problem_id}/statement.html"
    params["problem"] = session.query(Problem).filter(Problem.id == problem_id).first()
    params["form"] = form
    if form.validate_on_submit():
        code = request.form["code_area"]
        if code == "":
            params["message"] = "You can't submit empty code"
            return render_template('problem.html', **params)
        if not current_user.is_authenticated:
            params["message"] = "You must sign in to submit code"
            return render_template('problem.html', **params)
        return redirect('/practice/basic_programming')
    return render_template('problem.html', **params)


if __name__ == '__main__':
    main()
    print('wa')
