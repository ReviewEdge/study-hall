###############################################################################
# Imports
###############################################################################

import os
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_dir)

from flask import Flask, request, render_template, redirect, url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy

# user authentication
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user
from password_hasher import PasswordHasher
from forms.loginforms import RegisterForm, LoginForm

###############################################################################
# Basic Configuration
###############################################################################

# load files
dbfile = os.path.join(script_dir, "study_hall.sqlite3")
pepfile = os.path.join(script_dir, "pepper.bin")

# get pepper
with open(pepfile, 'rb') as fin:
  pepper_key = fin.read()

# set up password hasher
pwd_hasher = PasswordHasher(pepper_key)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'correcthorsebatterystaple'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Prepare and connect the LoginManager to this app
app.login_manager = LoginManager()
app.login_manager.login_view = 'get_login'
@app.login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

###############################################################################
# Database Setup
###############################################################################

# Create a database model for Users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary) # hash is a binary attribute

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("password is a write-only attribute")
    @password.setter
    def password(self, pwd):
        self.password_hash = pwd_hasher.hash(pwd)
    
    # add a verify_password convenience method
    def verify_password(self, pwd):
        return pwd_hasher.check(pwd, self.password_hash)

with app.app_context():
    db.create_all() # this is only needed if the database doesn't already exist

###############################################################################
# Route Handlers
###############################################################################

# User registration
@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template('/account/register.html', form=form)

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        # check if there is already a user with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if the email address is free, create a new user and send to login
        if user is None:
            user = User(name=form.name.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('get_login'))
        else: # if the user already exists
            # flash a warning message and redirect to get registration form
            flash('There is already an account with that email address')
            return redirect(url_for('get_register'))
    else: # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

@app.get('/login/')
def get_login():
    form = LoginForm()
    return render_template('/account/login.html', form=form)

# user login
@app.post('/login/')
def post_login():
    form = LoginForm()
    if form.validate():
        # try to get the user associated with this email address
        user = User.query.filter_by(email=form.email.data).first()
        # if this user exists and the password matches
        if user is not None and user.verify_password(form.password.data):
            # log this user in through the login_manager
            login_user(user)
            # redirect the user to the page they wanted or the home page
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        else: # if the user does not exist or the password is incorrect
            # flash an error message and redirect to login form
            flash('Invalid email address or password')
            return redirect(url_for('get_login'))
    else: # if the form was invalid
        # flash error messages and redirect to get login form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_login'))

# user log out
@app.get('/logout/')
@login_required
def get_logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

# user account
@app.get('/account')
@login_required
def account():
    return render_template('account/edit.html')

# home page
@app.get('/')
def index():
    return render_template('index.html', current_user=current_user)

# notes
@app.get('/notes')
@login_required
def notes_index():
    return render_template('notes/index.html')
