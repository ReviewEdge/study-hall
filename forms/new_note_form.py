from flask_wtf import FlaskForm
from wtforms.fields import SubmitField

class NewNoteForm(FlaskForm):
    submit = SubmitField("New Note")
