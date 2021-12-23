import cryptocode
import pyqrcode
from flask import Blueprint, Flask, render_template, redirect, flash, session, url_for
from flask_login import current_user, login_user, logout_user
from globals import ds_client
from io import BytesIO
from twofactorauth.config import *

# Blueprint Configuration
twofactorauth_bp = Blueprint(
    'twofactorauth_bp', __name__,
    url_prefix='/tfh',
    template_folder='templates',
    static_folder='static'
)


@twofactorauth_bp.route('/<workout_id>')
def twofactorhome(workout_id):
    page_template = 'welcome.html'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == '2fa':
        decrypt_key = workout['assessment']['key']
        encrypted_flag = 'IpmnWmd6aeyrsrCmcaljIVU19XOmFOKtr9B3OXChIbbZXbQ=*lbG7TJXiAIIS8cQtG9Nufw==*wrSgLeSlwVSCzwm' \
                         'rlpRlRQ==*c6Oj6lsCnrwLVIXgp0c6vg=='
        flag = str(cryptocode.decrypt(encrypted_flag, decrypt_key))
        return render_template(page_template, flag=flag, workout_id=workout_id)
    else:
        return redirect(404)


@twofactorauth_bp.route('/register/<workout_id>', methods=['GET', 'POST'])
def register(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == '2fa':
        """User registration route."""
        if current_user.is_authenticated:
            # if user is logged in we get out of here
            return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None:
                flash('Username already exists.')
                return redirect(url_for('twofactorauth_bp.register'))
            # add new user to the database
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            # redirect to the two-factor auth page, passing username in session
            session['username'] = user.username
            return redirect(url_for('twofactorauth_bp.two_factor_setup', workout_id=workout_id))
        return render_template('register.html', form=form, workout_id=workout_id)
    else:
        return redirect(404)


@twofactorauth_bp.route('/twofactor/<workout_id>')
def two_factor_setup(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == '2fa':
        if 'username' not in session:
            return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
        user = User.query.filter_by(username=session['username']).first()
        if user is None:
            return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
        # since this page contains the sensitive qrcode, make sure the browser
        # does not cache it
        return render_template('two-factor-setup.html', workout_id=workout_id), 200, {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'}
    else:
        return redirect(404)


@twofactorauth_bp.route('/qrcode')
def qrcode():
    if 'username' not in session:
        redirect(404)
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        redirect(404)

    # for added security, remove username from session
    del session['username']

    # render qrcode
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@twofactorauth_bp.route('/login/<workout_id>', methods=['GET', 'POST'])
def login(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == '2fa':
        """User login route."""
        if current_user.is_authenticated:
            # if user is logged in we get out of here
            return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.verify_password(form.password.data) or \
                    not user.verify_totp(form.token.data):
                flash('Invalid username, password or token.')
                return redirect(url_for('twofactorauth_bp.login', workout_id=workout_id))

            # log user in
            login_user(user)
            flash('You are now logged in!')
            return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
        return render_template('login.html', form=form, workout_id=workout_id)
    else:
        return redirect(404)


@twofactorauth_bp.route('/logout/<workout_id>')
def logout(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == '2fa':
        """User logout route."""
        logout_user()
        return redirect(url_for('twofactorauth_bp.twofactorhome', workout_id=workout_id))
    else:
        return redirect(404)


@twofactorauth_bp.errorhandler(404)
def page_not_found_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


@twofactorauth_bp.errorhandler(500)
def internal_server_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)
