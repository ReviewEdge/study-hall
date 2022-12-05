from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, HiddenField
from wtforms.validators import InputRequired

class ShareNoteForm(FlaskForm):
    submit = SubmitField("Share")
