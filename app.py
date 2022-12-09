###############################################################################
# Imports
###############################################################################

import os
import sys
import time

from flask.helpers import abort
script_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_dir)

from flask import Flask, request, render_template, redirect, url_for
from flask import flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func

# user authentication
from flask_login import UserMixin, LoginManager, login_required
from flask_login import login_user, logout_user, current_user
from password_hasher import PasswordHasher
from forms.account_forms import RegisterForm, LoginForm, EditAccountForm
from forms.new_note_form import NewNoteForm
from forms.new_studyset_form import NewStudysetForm
from forms.share_note_form import ShareNoteForm

from werkzeug.utils import secure_filename

###############################################################################
# Basic Configuration
###############################################################################

UPLOAD_FOLDER = 'static/images/user_uploads'
ALLOWED_EXTENSIONS = {'jpeg','jpg','jpe','jfi','jif','jfif','png','gif','bmp','webp'} # match Tiny MCE editor

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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# make current_user available on all pages without passing it in to each template every time
@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)

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
    notes = db.relationship('Note', backref='owner')
    study_sets = db.relationship('StudySet', backref='owner')

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

# Create database model for Study Sets
class StudySet(db.Model):
    __tablename__ = 'StudySets'
    id = db.Column(db.Integer, primary_key=True)
    ownerID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Unicode, nullable=False)
    flashcards = db.relationship('Flashcard', backref='study_set')

# Create database model for flashcards
class Flashcard(db.Model):
    __tablename__ = 'Flashcards'
    id = db.Column(db.Integer, primary_key=True)
    setID = db.Column(db.Integer, db.ForeignKey('StudySets.id'), nullable=False)
    front_text = db.Column(db.Unicode, nullable=False)
    back_text = db.Column(db.Unicode, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def to_json(self):
	    return {
			"id": self.id,
			"setID": self.setID,
			"timestamp": self.timestamp.isoformat(),
			"frontText": self.front_text,
			"backText": self.back_text,
		}

# Create database model for note
class Note(db.Model):
    __tablename__ = 'Notes'
    id = db.Column(db.Integer, primary_key=True)
    ownerID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Unicode)
    word_count = db.Column(db.Integer, nullable=False, default=0)
    content = db.Column(db.Unicode)
    public = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

with app.app_context():
    db.create_all() # this is only needed if the database doesn't already exist

###############################################################################
# Route Handlers
###############################################################################

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_filename(filename):
    return filename.rsplit('.', 1)

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
            login_user(user)
            flash("Account created. Welcome!")
            return redirect(url_for('index'))
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
def get_account():
    form = EditAccountForm()
    return render_template('account/edit.html', form=form)

@app.post('/account')
@login_required
def post_account():
    form = EditAccountForm()
    if form.validate():
        user = load_user(current_user.get_id())
        if user.verify_password(form.current_password.data):
            user.name = form.name.data
            user.email = form.email.data
            if form.new_password.data is not None and form.new_password.data != "":
                user.password = form.new_password.data
            db.session.commit()
            flash("Account updated")
        else:
            flash("Current password is not correct")
    else: # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
    return redirect(url_for('get_account'))

@app.delete('/api/account')
@login_required
def delete_account():
    user = load_user(current_user.get_id())
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted')
    return "success", 200

# home page
@app.get('/')
def index():
    return render_template('index.html')

# notes
@app.get('/notes')
@login_required
def get_notes():
    form = NewNoteForm()
    notes = Note.query.filter_by(ownerID = current_user.get_id()).order_by(Note.updated_at.desc()).all()
    return render_template('notes/index.html', form=form, notes=notes)

@app.post('/notes/create')
@login_required
def post_create_note():
    note = Note(ownerID=current_user.get_id())
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('get_edit_note', id=note.id))

@app.get('/notes/<int:id>/edit')
@login_required
def get_edit_note(id):
    note = Note.query.get_or_404(id)
    form = ShareNoteForm()
    form.page.data = "edit"
    share_link = f"{request.host_url}{url_for('get_view_note', id=note.id)[1:]}"

    # require ownership of the note
    if note.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('index'))

    return render_template('notes/edit.html', note=note, form=form, share_link=share_link)

@app.patch('/api/notes/<int:id>')
@login_required
def update_note(id):
    note = Note.query.get_or_404(id)

    # require ownership of the note
    if note.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('index'))

    note_json = request.get_json()
    note.title = note_json.get('title')
    note.word_count = note_json.get('wordCount')
    note.content = note_json.get('content')
    # note.updated_at = datetime.now()
    db.session.commit()
    return "success", 200

@app.get('/notes/<int:id>/view')
def get_view_note(id):
    note = Note.query.get_or_404(id)
    form = ShareNoteForm()
    form.page.data = "view"
    share_link = f"{request.host_url}{url_for('get_view_note', id=note.id)[1:]}"

    # require either public or ownership of the note
    if not note.public and (current_user.is_anonymous or note.ownerID != int(current_user.get_id())):
        flash("You are not the owner!")
        return redirect(url_for('index'))

    is_owner = current_user.is_authenticated and note.ownerID == int(current_user.get_id())

    return render_template('notes/view.html', note=note, form=form, share_link=share_link, is_owner=is_owner)

@app.post('/notes/<int:id>/share')
@login_required
def post_share_note(id):
    note = Note.query.get_or_404(id)
    form = ShareNoteForm()

    # require ownership of the note
    if note.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('index'))

    note.public = not note.public
    # note.updated_at = datetime.now()
    db.session.commit()

    if form.page.data == "view":
        return redirect(url_for('get_view_note', id=note.id))
    else:
        return redirect(url_for('get_edit_note', id=note.id))

@app.delete('/api/notes/<int:id>')
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)

    # require ownership of the note
    if note.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return "not authorized", 403

    db.session.delete(note)
    db.session.commit()
    flash('Note has been deleted')
    return "success", 200

@app.post('/api/upload_file')
@login_required
def upload_file():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        # validate and generate path
        filename = secure_filename(file.filename)
        split = split_filename(filename)
        filename = secure_filename(f'{split[0].lower()}-{time.time()}.{split[1].lower()}')

        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # save image
        file.save(img_path)

        # return image
        return jsonify({"location": filename})

    return "failure", 404

# flashcards
@app.get('/flashcards')
@login_required
def get_flashcards():
    study_sets = load_user(current_user.get_id()).study_sets
    return render_template('flashcards/index.html', study_sets=study_sets)


@app.get('/newstudyset')
@login_required
def get_new_studyset():
    form = NewStudysetForm()
    return render_template("/flashcards/post_studyset.html", form=form)


@app.post('/newstudyset')
@login_required
def post_new_studyset():
    form = NewStudysetForm()
    if form.validate():
        new_study_set = StudySet(
            ownerID = current_user.get_id(),
            name= form.name.data
        )

        db.session.add(new_study_set)
        db.session.commit()
        return redirect(url_for('get_flashcards'))

    else: # if the form was invalid
        # flash error messages and redirect to get registration form again
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_new_studyset'))


@app.post('/api/flashcard/create/<int:id>/')
@login_required
def post_create_flashcard(id):
    owner = StudySet.query.get_or_404(id).ownerID

    # require ownership of the study set
    if owner != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('get_flashcards'))

    new_flashcard = Flashcard(
        setID=id,
        front_text = "Front Text",
        back_text = "Back Text",
        timestamp = datetime.now()
    )
    db.session.add(new_flashcard)
    db.session.commit()
    return jsonify(new_flashcard.to_json()), 201


@app.get("/api/flashcards/<int:id>/")
def get_studyset_flashcards(id):
    study_set = StudySet.query.get_or_404(id)

    # require ownership of the study set
    if study_set.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('get_flashcards'))

    flashcards = study_set.flashcards

    return jsonify({
		"count": len(flashcards),
		"flashcards": [f.to_json() for f in flashcards]
	})


@app.get('/flashcards/<int:id>')
def get_view_study_set(id):
    study_set = StudySet.query.get_or_404(id)

    # require ownership of the study set
    if study_set.ownerID != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('get_flashcards'))

    return render_template('flashcards/view2.html', study_set=study_set)


@app.patch('/api/flashcard/<int:id>')
@login_required
def update_single_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)

    # would be better to have ownerID in each flashcard model
    owner = StudySet.query.get_or_404(flashcard.setID).ownerID

    # require ownership of the study set
    if owner != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('get_flashcards'))

    flashcard_json = request.get_json()
    flashcard.front_text = flashcard_json.get('frontText')
    flashcard.back_text = flashcard_json.get('backText')
    db.session.commit()
    return "success", 200


@app.get('/api/flashcard/<int:id>/view')
@login_required
def get_single_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)

    # would be better to have ownerID in each flashcard model
    owner = StudySet.query.get_or_404(flashcard.setID).ownerID

    # require ownership of the study set
    if owner != int(current_user.get_id()):
        flash("You are not the owner!")
        return redirect(url_for('get_flashcards'))

    return jsonify(flashcard.to_json()), 201


@app.get('/api/study/<int:id>')
@login_required
def study_studyset(id):
    try:
        pos = session[f"pos_in_set_{id}"]
        study_set = StudySet.query.get_or_404(id)

        # require ownership of the study set
        if study_set.ownerID != int(current_user.get_id()):
            flash("You are not the owner!")
            return redirect(url_for('get_flashcards'))

        session[f"last_in_set_{id}"] = len(study_set.flashcards) - 1
        if(session[f"last_in_set_{id}"] == -1):
            return render_template('flashcards/study/view.html', study_set=study_set, current_flashcard=False)
        return render_template('flashcards/study/view.html', study_set=study_set, current_flashcard=study_set.flashcards[pos])
    except KeyError:
        study_set = StudySet.query.get_or_404(id)

        # require ownership of the study set
        if study_set.ownerID != int(current_user.get_id()):
            flash("You are not the owner!")
            return redirect(url_for('get_flashcards'))

        session[f"pos_in_set_{id}"] = 0
        session[f"last_in_set_{id}"] = len(study_set.flashcards) - 1
        if(session[f"last_in_set_{id}"] == -1):
            return render_template('flashcards/study/view.html', study_set=study_set, current_flashcard=False)
        return render_template('flashcards/study/view.html', study_set=study_set, current_flashcard=study_set.flashcards[session[f"pos_in_set_{id}"]])


@app.get('/api/study/<int:id>/next')
@login_required
def study_studyset_next(id):
    try:
        if session[f"pos_in_set_{id}"] == session[f"last_in_set_{id}"]:
            session[f"pos_in_set_{id}"] = 0
        else:
            session[f"pos_in_set_{id}"] += 1
        return study_studyset(id)
    except KeyError:
        return study_studyset(id)


@app.get('/api/study/<int:id>/prev')
@login_required
def study_studyset_prev(id):
    try:
        if session[f"pos_in_set_{id}"] == 0:
            session[f"pos_in_set_{id}"] = session[f"last_in_set_{id}"]
        else:
            session[f"pos_in_set_{id}"] -= 1
        return study_studyset(id)
    except KeyError:
        return study_studyset(id)

###############################################################################
# Timer Data Handling
###############################################################################

#this is used by the timer's javascript whenever a 
#new page is loaded to query the current state of the timer
@app.get('/timer/status/')
def status():
    #send following data
    #{
    #   "a": active? (true=running, false=paused)
    #   "w": working? (true=working, false=break)
    #   "s": start time (only sent if running)
    #   "t": time left in seconds (if start time is included, then remove time passed since starting)
    #   "c": cycle number (how many work sessions have been completed)
    #}
    #added "t-" to the start of the variable name so it won't accidentially mess someone else's session variable
    if('t-time-left' not in session):
        session['t-active'] = False
        session['t-working'] = True
        session['t-start'] = "None"
        session['t-time-left'] = 1500
        session['t-cycle'] = 0
    
    value = {
        "a": session['t-active'],
        "w": session['t-working'],
        "s": session['t-start'],
        "t": session['t-time-left'],
        "c": session['t-cycle']
    }
    return jsonify(value)


#the javascript uses this to log the fact that it has stopped the timer,
#as well as what state the timer is in (how much time is left)
#this is also called when the timer finishes to set up the next one
@app.post('/timer/pause/')
def pause():
    data = request.get_json()
    #print(f"w={data.get('w')} t={data.get('t')}")
    session['t-working'] = data.get('w')
    session['t-time-left'] = data.get('t')
    session['t-active'] = False
    session['t-cycle'] = data.get('c', session['t-cycle'])
    return "", 200

@app.post('/timer/start/')
def start():
    data = request.get_json()
    #print(f"s={data.get('s')} t={data.get('t')}")
    session['t-start'] = data.get('s')
    session['t-time-left'] = data.get('t')
    session['t-active'] = True
    return "", 200