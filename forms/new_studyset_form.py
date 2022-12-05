from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from wtforms.validators import InputRequired, Length

class NewStudysetForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=5000)])
    submit = SubmitField("Submit")