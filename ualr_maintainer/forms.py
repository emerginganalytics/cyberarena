from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class CreateWorkoutForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    unit = StringField('Lesson Name (for future reference)', validators=[DataRequired()])
    team = IntegerField('Select number of teams (between 1 and 10)', validators=[DataRequired()])
    length = IntegerField('Select length of availability (between 1 and 7 days)', validators=[DataRequired()])

class StartVMForm(FlaskForm):
    time = IntegerField('How long should the workout run (1 - 10 hours)?', validators=[DataRequired(), NumberRange(min=1, max=10, message="Please select a value between 1 and 10")])

class StopVMForm(FlaskForm):
    submit = SubmitField('Stop VM')