from flask import Flask, request, render_template, redirect, url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy

import os
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_dir)

dbfile = os.path.join(script_dir, "study_hall.sqlite3")

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'correcthorsebatterystaple'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbfile}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# TODO: models here

with app.app_context():
  db.create_all()

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/notes')
def notes_index():
    return render_template('notes/index.html')

@app.get('/account')
def account():
    return render_template('account/edit.html')
