from flask import Flask, render_template, redirect, flash, request, session, abort, url_for, jsonify
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from google.cloud import datastore

import onetimepass
import pyqrcode
import os
import base64
import requests
import random
import string

# application instance
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.urandom(12)


# initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)


class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    otp_secret = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        return 'otpauth://totp/CyberGym:{0}?secret={1}&issuer=CyberGym2FA' \
            .format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)


@lm.user_loader
def load_user(user_id):
    """User loader callback for Flask-Login."""
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password again',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    token = StringField('Token', validators=[DataRequired(), Length(6, 6)])
    submit = SubmitField('Login')


ds_client = datastore.Client()
project = 'ualr-cybersecurity'


def set_workout_flag(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    flag_wireshark = 'CyberGym{'.join(random.choices(string.ascii_letters + string.digits, k=16,)) + '}'
    workout['container_info']['wireshark_flag'] = flag_wireshark
    ds_client.put(workout)
    return flag_wireshark


def publish_status(workout_id, workout_key):
    url = 'https://buildthewarrior.cybergym-eac-ualr.org/complete'

    status = {
        "workout_id": workout_id,
        "token": workout_key,
    }

    publish = requests.post(url, json=status)
    print('[*] POSTING to {} ...'.format(url))
    print(publish)


def check_flag(workout_id, submission):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    # data is a dict list that is passed back to page as JSON object
    status = workout['assessment']['questions']
    data = {
        'wireshark_flag': {
            'flag': workout['container_info']['wireshark_flag'],
            'status': status[2]['complete']
        }
    }

    flag_wireshark = workout['container_info']['wireshark_flag']

    if submission in flag_wireshark:
        data['wireshark_flag']['status'] = True
        workout_key = workout['assessment']['questions'][2]['1TkkG1J']
        publish_status(workout_id, workout_key)

    return data


@app.route('/<workout_id>')
def home(workout_id):
    if not session.get('logged_in'):
        return render_template('index.html', workout_id=workout_id)
    else:
        set_workout_flag(workout_id)
        return redirect('/flag/' + workout_id)


# Generates values based on workout
@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'wireshark' or 'dos':
            return redirect('/' + workout_id)
        elif workout['type'] == 'xss':
            return redirect('/workouts/xss/' + workout_id)
        elif workout['type'] == '2fa':
            return redirect('/workouts/tfh/' + workout_id)
    else:
        return redirect('/invalid')


@app.route("/login/<workout_id>", methods=["GET", "POST"])
def do_admin_login(workout_id):
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return redirect(url_for('home', workout_id=workout_id))


@app.route("/flag/<workout_id>", methods=["GET", "POST"])
def flag(workout_id):
    page_template = 'flag.html'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    # Only valid workouts can access
    if workout:
        if workout['type'] == 'wireshark':
            wireshark_flag = workout['container_info']['wireshark_flag']

            if request.method == 'GET':
                return render_template(
                    page_template,
                    workout_id=workout_id,
                    wireshark_flag=wireshark_flag
                )
            elif request.method == 'POST':
                plaintext = request.get_json()
                data = check_flag(workout_id, str(plaintext['flag']))

                return jsonify({
                    'message': data['wireshark_flag']['flag'],
                    'status': data['wireshark_flag']['status'],
                })
        else:
            return redirect('/invalid')
    else:
        return redirect('/invalid')


@app.route('/invalid', methods=['GET'])
def invalid():
    template = 'invalid_workout.html'
    return render_template(template)


@app.route("/logout/<workout_id>", methods=["GET", "POST"])
def admin_logout(workout_id):
    session['logged_in'] = False
    return redirect(url_for('home', workout_id=workout_id))


@app.route("/workouts/<workout_id>", methods=["POST"])
def workouts(workout_id):
    return render_template('workouts.html', workout_id=workout_id)


@app.route("/workouts/xss/<workout_id>", methods=["GET", "POST"])
def xss(workout_id):
    return render_template('xss_d.html', workout_id=workout_id)


@app.route('/workouts/tfh/<workout_id>')
def twofactorhome(workout_id):
    return render_template('welcome.html', workout_id=workout_id)


@app.route('/workouts/tfh/register/<workout_id>', methods=['GET', 'POST'])
def register(workout_id):
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register', workout_id=workout_id))
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup', workout_id=workout_id))
    return render_template('register.html', form=form, workout_id=workout_id)


@app.route('/workouts/tfh/twofactor/<workout_id>')
def two_factor_setup(workout_id):
    if 'username' not in session:
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html', workout_id=workout_id), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/qrcode')
def qrcode():
    if 'username' not in session:
        abort(404)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        abort(404)

    # for added security, remove username from session
    del session['username']

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/workouts/tfh/login/<workout_id>', methods=['GET', 'POST'])
def login(workout_id):
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('login', workout_id=workout_id))

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    return render_template('login.html', form=form, workout_id=workout_id)


@app.route('/workouts/tfh/logout/<workout_id>')
def logout(workout_id):
    """User logout route."""
    logout_user()
    return redirect(url_for('twofactorhome', workout_id=workout_id))


# create database tables if they don't exist yet
db.create_all()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)

