from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class TasksForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    done = BooleanField("Is Done?")
    submit = SubmitField('Submit')
