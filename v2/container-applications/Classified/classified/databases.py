import base64
import sqlite3
import os
import hashlib
import sqlite3
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    token = StringField('Token', validators=[DataRequired(), Length(6, 6)])
    submit = SubmitField('Login')


class SQLInjection:
    def __init__(self):
        self.db = 'bad.db'

    def connect(self):
        return sqlite3.connect(self.db)

    @staticmethod
    def _hash_pass(pwd):
        m = hashlib.md5()
        m.update(pwd.encode('utf-8'))
        return m.hexdigest()

    def _populate(self):
        with self.connect() as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE employees(username TEXT, password TEXT)""")
            c.execute('INSERT INTO employees VALUES("RickAstley", "{}")'.format(self._hash_pass("NeverGonnaGiveYouUp")))
            c.execute('INSERT INTO employees VALUES("SuperSecretClassifiedEmployee", "{}")'.format(self._hash_pass("password")))
            c.execute('INSERT INTO employees VALUES("BigBossAdmin", "{}")'.format(self._hash_pass("kittycat222")))
            connection.commit()


class XSS:
    def __init__(self):
        self.db = 'xss_s.db'

    def connect(self):
        xss_db = sqlite3.connect(self.db)
        xss_db.cursor().execute("""CREATE TABLE IF NOT EXISTS feedbacks (workout_ids TEXT, feedback TEXT)""")
        xss_db.commit()
        return xss_db

    def add_feedback(self, feedback, workout_id):
        xss_db = self.connect()
        xss_db.cursor().execute("""INSERT INTO feedbacks (workout_ids, feedback) VALUES (?, ?) """, (workout_id, feedback,))
        xss_db.commit()

    def get_feedback(self, workout_id, search_query=None):
        xss_db = self.connect()
        results = []
        for (feedback,) in xss_db.cursor().execute("""SELECT feedback FROM feedbacks WHERE workout_ids=?""", (workout_id,)).fetchall():
            if search_query is None or search_query in feedback:
                results.append(feedback)
        return results
