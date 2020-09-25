from flask import Flask, render_template, redirect, flash, request, session, abort, url_for, jsonify, g
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from google.cloud import datastore, runtimeconfig

import hashlib
import sqlite3
import onetimepass
import pyqrcode
import os
import base64

# TODO: Server Side Template Injection
# application instance
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.urandom(12)


# initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
app.database = "bad.db"
ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")


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
        return 'otpauth://totp/CyberGym:{0}?secret={1}&issuer=CyberGym2FA'.format(self.username, self.otp_secret)

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


def connect_db():
    return sqlite3.connect(app.database)


def hash_pass(passw):
    m = hashlib.md5()
    m.update(passw.encode('utf-8'))
    return m.hexdigest()


def connect_xssdb():
    xssdb = sqlite3.connect('xss_s.db')
    xssdb.cursor().execute("""CREATE TABLE IF NOT EXISTS feedbacks (workout_ids TEXT, feedback TEXT)""")
    xssdb.commit()
    return xssdb


def add_feedback(feedback, workout_id):
    xssdb = connect_xssdb()
    xssdb.cursor().execute("""INSERT INTO feedbacks (workout_ids, feedback) VALUES (?, ?) """, (workout_id, feedback,))
    xssdb.commit()


def get_feedbacks(workout_id, search_query=None):
    xssdb = connect_xssdb()
    results = []
    for (feedback,) in \
            xssdb.cursor().execute("""SELECT feedback FROM feedbacks WHERE workout_ids=?""", (workout_id,)).fetchall():
        if search_query is None or search_query in feedback:
            results.append(feedback)
    return results


@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    app.logger.info('workout_type : %s' % workout['type'])

    if workout:
        if workout['type'] == 'wireshark' or 'dos':
            return redirect('/' + workout_id)
        elif workout['type'] == 'xss':
            return redirect('/workouts/xss/' + workout_id)
        elif workout['type'] == 'Two-Step':
            return redirect('/workouts/tfh/' + workout_id)
        elif workout['type'] == 'inspect':
            return redirect('/workouts/inspect' + workout_id)
        elif workout['type'] == 'sql':
            return redirect('/workouts/sql_injection' + workout_id)
    else:
        return redirect(404)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        wireshark_flag = "CyberGym{Classified_Shark_Week}"
        return render_template('flag.html', wireshark_flag=wireshark_flag)


@app.route("/login", methods=["GET", "POST"])
def do_admin_login():
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return redirect(url_for('home'))


@app.route('/invalid', methods=['GET'])
def invalid():
    template = 'invalid_workout.html'
    return render_template(template)


@app.route("/logout", methods=["GET", "POST"])
def admin_logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/workouts", methods=["POST"])
def workouts():
    return render_template('workouts.html')


@app.route("/workouts/xss/<workout_id>", methods=["GET", "POST"])
def xss(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'xss':
        page_template = 'xss.html'
        name = 'Stranger'
        bad_request = 'bad request'
        if request.args.get('bad_request'):
            bad_request = request.args.get('bad_request')

        return render_template(page_template, name=name, bad_request=bad_request, workout_id=workout_id)
    else:
        return redirect(404)


@app.route("/workouts/xss_r/<workout_id>", methods=['GET', 'POST'])
def xss_r(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'xss':
        page_template = 'xss_r.html'
        name = 'Stranger'
        if request.method == 'POST':
            name = request.form['name']
        return render_template(page_template, name=name, workout_id=workout_id)
    else:
        return redirect(404)


@app.route("/workouts/xss_s/<workout_id>", methods=['GET', 'POST'])
def xss_s(workout_id):
    key = ds_client.key('cybergym-workout', workout_id, use_cache=False, use_memcache=False)
    workout = ds_client.get(key)
    if workout['type'] == 'xss':
        page_template = 'xss_s.html'
        if request.method == 'POST':
            add_feedback(request.form['feedback'], workout_id)

        search_query = request.args.get('query')

        feedbacks = get_feedbacks(workout_id, search_query)

        return render_template(page_template, feedbacks=feedbacks, search_query=search_query, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/workouts/tfh/<workout_id>')
def twofactorhome(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'Two-Step':
        page_template = 'welcome.html'
        flag = 'CyberGym{Classified_Authentication}'
        return render_template(page_template, flag=flag, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/workouts/tfh/register/<workout_id>', methods=['GET', 'POST'])
def register(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'Two-Step':
        """User registration route."""
        if current_user.is_authenticated:
            # if user is logged in we get out of here
            return redirect(url_for('twofactorhome', workout_id=workout_id))
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
            return redirect(url_for('two_factor_setup', workout_id=workout_id))
        return render_template('register.html', form=form, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/workouts/tfh/twofactor/<workout_id>')
def two_factor_setup(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'Two-Step':
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
    else:
        return redirect(404)


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
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'Two-Step':
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
    else:
        return redirect(404)


@app.route('/workouts/tfh/logout/<workout_id>')
def logout(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'Two-Step':
        """User logout route."""
        logout_user()
        return redirect(url_for('twofactorhome', workout_id=workout_id))
    else:
        return redirect(404)


@app.route('/inspect/<workout_id>')
def inspect(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'inspect':
        page_template = 'inspect.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/sql/<workout_id>')
def sql_injection(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout_id['type'] == 'sql':
        page_template = 'sql.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@app.route('/login_SQL', methods=['POST'])
def login_sql():
    if request.method == 'POST':
        uname, pword = (request.json['username'], request.json['password'])
        g.db = connect_db()
        cur = g.db.execute("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %
                           (uname, hash_pass(pword)))
        if cur.fetchone():
            result = {'status': 'success',
                      'flag': 'CyberGym{jFt6EjlH6I8EcfBg}'}
        else:
            result = {'status': 'fail'}
        g.db.close()
        return jsonify(result)

# TODO: Update invalid.html to be pretty and show errors
@app.errorhandler(404)
def page_not_found_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


@app.errorhandler(500)
def internal_server_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


# create database tables if they don't exist yet

# create db for 2fa
db.create_all()
# create bad database for SQL Injection
if not os.path.exists(app.database):
    with sqlite3.connect(app.database) as connection:
        c = connection.cursor()
        c.execute("""CREATE TABLE employees(username TEXT, password TEXT)""")
        c.execute('INSERT INTO employees VALUES("RickAstley", "{}")'.format(hash_pass("NeverGonnaGiveYouUp")))
        c.execute('INSERT INTO employees VALUES("SuperSecretClassifiedEmployee", "{}")'.format(hash_pass("password")))
        c.execute('INSERT INTO employees VALUES("BigBossAdmin", "{}")'.format(hash_pass("kittycat222")))
        connection.commit()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)

