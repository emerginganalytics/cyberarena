from flask import Flask, render_template, redirect, flash, request, session, abort
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length, EqualTo
import onetimepass
import pyqrcode
import os
import base64
app = Flask(__name__)
app.secret_key = os.urandom(12)


# initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)


class User(UserMixin, db.Model):
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
        return 'otpauth://totp/2FA-Demo:{0}?secret={1}&issuer=2FA-Demo' \
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


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('workouts.html')


@app.route("/login", methods=["GET", "POST"])
def do_admin_login():
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return home()


@app.route("/flag", methods=["POST"])
def flag():
    return render_template('flag.html')


@app.route("/logout", methods=["GET", "POST"])
def admin_logout():
    session['logged_in'] = False
    return home()


@app.route("/workouts", methods=["POST"])
def workouts():
    return render_template('workouts.html')


@app.route("/workouts/xss_d", methods=["GET", "POST"])
def xss_d():
    return render_template('xss_d.html')


@app.route("/workouts/xss_r", methods=["GET", "POST"])
def xss_r():
    return render_template('xss_r.html')


@app.route("/workouts/xss_s", methods=["GET", "POST"])
def xss_s():
    return render_template('xss_s.html')


@app.route('/workouts/two-factor-home')
def index():
    return render_template('two_factor.html')

@app.route('/twofactor')
def two_factor_setup():
    if 'username' not in session:
        return redirect(index)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(index)
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}



@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(register)
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(register)
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(two_factor_setup)
    return render_template('register.html', form=form)


@app.route('/qrcode')
def qrcode():
    if 'username' not in session:
        abort(404)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        abort(404)


    del session['username']


    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/workouts/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(index)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(login)

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(index)
    return render_template('login.html', form=form)


@app.route('/workouts/logout')
def logout():
    """User logout route."""
    logout_user()
    return redirect(index)


# create database tables if they don't exist yet
db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)

