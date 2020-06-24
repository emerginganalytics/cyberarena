from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Email

class CreateWorkoutForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    unit = StringField('Lesson Name (for future reference)', validators=[DataRequired()])
    team = IntegerField('Select number of students (between 1 and 10)', validators=[DataRequired()])
    length = IntegerField('Select length of availability (between 1 and 100 days)', validators=[DataRequired()])

class CreateExpoForm(FlaskForm):
    unit = StringField('What is your name?', validators=[DataRequired()])
    email = StringField(default='expo@ualr.edu')
    team = IntegerField(default=1)
    length = IntegerField(default=1)