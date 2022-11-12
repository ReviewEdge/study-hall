from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, SubmitField, EmailField, StringField
from wtforms.validators import InputRequired, Email, EqualTo, Length, Optional

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=256)])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo('password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=256)])
    submit = SubmitField("Login")

class EditAccountForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    new_password = PasswordField("New Password", validators=[Optional(), Length(min=8, max=256)])
    confirm_new_password = PasswordField("Confirm New Password", validators=[EqualTo('new_password')])
    current_password = PasswordField("Current Password", validators=[InputRequired(), Length(min=8, max=256)])
    submit = SubmitField("Update")
