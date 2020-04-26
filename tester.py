from PIL import Image
from flask import Flask, render_template, url_for, redirect, request, session, abort, make_response, jsonify
from flask_login import LoginManager, current_user

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


@app.route("/")
def start_page():
    return redirect('/home')


@app.route("/home")
def home_page():
    params = {
        "main_css": url_for('static', filename='css/main.css'),
        "title": "Home page",
    }
    if current_user.is_authenticated:
        params["user_icon"] = url_for('data', filename=f'user_data/icons/{current_user.icon_id}.png')
    return render_template("home_page.html", **params)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    def resize_image(path):
        image = Image.open(path)
        image = image.resize((64, 64))
        image.save(path)

    def generate_icon_name():
        save_path = "data/user_data/icons"
        icon_id = randint(100000000, 999999999)
        icon_name = f"{icon_id}.png"
        while icon_name in os.listdir(save_path):
            icon_id = randint(100000000, 999999999)
            icon_name = f"{icon_id}.png"
        return icon_id, icon_name

    def save_custom_user_icon(img):
        icon_id, icon_name = generate_icon_name()
        path = f"data/user_data/icons/{icon_name}"
        open(path, 'wb').write(img.read())
        resize_image(path)

    def save_default_user_icon():
        num = randint(1, 3)  # 1-number of default icons
        icon_id, icon_name = generate_icon_name()
        path = f"data/user_data/icons/{icon_name}"
        open(path, 'wb').write(open(f"data/default/user_icons/user_icon_{num}.png", "rb").read())
        resize_image(path)

    # Removing Cache
    response = make_response(url_for('sign_up'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'

    form = SignUpForm()
    params = {
        "main_css": url_for('static', filename='css/main.css'),
        "title": "Sign up",
        "form": form
    }
    if current_user.is_authenticated:
        params["user_icon"] = url_for('data', filename=f'user_data/icons/{current_user.icon_id}.png')
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
        if form.icon.data.read() == b'':
            save_default_user_icon()
        else:
            save_custom_user_icon(form.icon.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/home')
    return render_template('sign_up.html', **params)


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    form = RegisterForm()
    params = {
        "main_css": url_for('static', filename='css/main.css'),
        "title": "Log in",
        "form": form
    }
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            params["password_error_message"] = "Password mismatch"
            return render_template('sign_up.html', **params)
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            params["username_error_message"] = "This username already exists"
            return render_template('sign_up.html', **params)
        if session.query(User).filter(User.email == form.email.data).first():
            params["email_error_message"] = "This email already exists"
            return render_template('sign_up.html', **params)
        user = User(
            login=form.login.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/home')
    return render_template('sign_up.html', **params)


if __name__ == '__main__':
    main()
