from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class CreateWorkoutForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    unit = StringField('Lesson Name (for future reference)', validators=[DataRequired()])
    team = IntegerField('Select number of teams (between 1 and 10)', validators=[DataRequired()])
    length = IntegerField('Select length of availability (between 1 and 100 days)', validators=[DataRequired()])