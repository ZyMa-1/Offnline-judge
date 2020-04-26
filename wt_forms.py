from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import PasswordField, StringField, SubmitField, FileField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SignUpForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat password', validators=[DataRequired()])
    icon = FileField("Choose image", validators=[FileAllowed(['jpg', 'png'], "Image")])
    submit = SubmitField('Submit')


class LogInForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')
