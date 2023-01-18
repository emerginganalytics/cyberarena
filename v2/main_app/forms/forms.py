from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField
from wtforms.validators import DataRequired


class CreateWorkoutForm(FlaskForm):
    email = HiddenField('Email')
    unit = StringField('Lesson Name (for future reference)', validators=[DataRequired()])
    team = IntegerField('Select number of students (between 1 and 10)', validators=[DataRequired()])
    length = IntegerField('Select length of availability (between 1 and 100 days)', validators=[DataRequired()])


class CreateUnitForm(FlaskForm):
    email = HiddenField('Email')


class CreateEscapeRoom(FlaskForm):
    pass

class CreateFixedArena(FlaskForm):
    pass

class CreateFixedArenaClass(FlaskForm):
    pass