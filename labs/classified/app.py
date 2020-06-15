from flask import Flask, render_template, redirect, flash, request, session, abort, url_for
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length, EqualTo
from server_scripts import ds_client

import onetimepass
import pyqrcode
import os
import base64


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
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    password_again = PasswordField('Password again',
                                   validators=[Required(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    token = StringField('Token', validators=[Required(), Length(6, 6)])
    submit = SubmitField('Login')


@app.route('/<workout_id>')
def home(workout_id):
    if not session.get('logged_in'):
        return render_template('index.html', workout_id=workout_id)
    else:
        return render_template('workouts.html', workout_id=workout_id)


# Generates values based on workout
@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'wireshark':
            return redirect('/home/' + workout_id)
        elif workout['type'] == 'xss':
            return redirect('/workouts/xss/' + workout_id)
        elif workout['type'] == '2fa':
            return redirect('/workouts/tfh/' + workout_id)
    else:
        return redirect('/invalid')


@app.route("/login", methods=["GET", "POST"])
def do_admin_login():
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return home()


@app.route("/flag/<workout_id>", methods=["POST"])
def flag(workout_id):
    return render_template('flag.html', workout_id=workout_id)


@app.route("/logout", methods=["GET", "POST"])
def admin_logout():
    session['logged_in'] = False
    return home()


@app.route("/workouts/<workout_id>", methods=["POST"])
def workouts(workout_id):
    return render_template('workouts.html', workout_id=workout_id)


@app.route("/workouts/xss/<workout_id>", methods=["GET", "POST"])
def xss(workout_id):
    return render_template('xss_d.html', workout_id=workout_id)


@app.route('/workouts/tfh/<workout_id>')
def twofactorhome(workout_id):
    return render_template('welcome.html')


@app.route('/workouts/tfh/register/<workout_id>', methods=['GET', 'POST'])
def register(workout_id):
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('twofactorhome'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup'))
    return render_template('register.html', form=form, workout_id=workout_id)


@app.route('/workouts/tfh/twofactor')
def two_factor_setup():
    if 'username' not in session:
        return redirect(url_for('twofactorhome'))
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('twofactorhome'))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html'), 200, {
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


@app.route('/workouts/tfh/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('twofactorhome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('login'))

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(url_for('twofactorhome'))
    return render_template('login.html', form=form, workout_id=workout_id)


@app.route('/workouts/tfh/logout')
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('twofactorhome'))


# create database tables if they don't exist yet
db.create_all()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)

