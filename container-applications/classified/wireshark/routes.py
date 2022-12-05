import cryptocode
from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from globals import ds_client

# Blueprint Configuration
wireshark_bp = Blueprint(
    'wireshark_bp', __name__,
    url_prefix='/wireshark',
    template_folder='email_templates',
    static_folder='static'
)


@wireshark_bp.route('/<workout_id')
def home(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if not session.get('logged_in'):
        return render_template('index.html', workout_id=workout_id)
    else:
        decrypt_key = workout['assessment']['key']
        encrypted_flag = 'w7w1HZQSOlQk7cxRjqICoIXkFbUsjnr9CHJkvZ51Iw==*9o+WrK5lFOZG70IARQ5HGA==*7bLeQoMR/IhXQjlvey' \
                         '71KQ==*D+iRjmWUsHXkKTC+G6cF4g=='
        wireshark_flag = cryptocode.decrypt(encrypted_flag, decrypt_key)
        return render_template('flag.html', wireshark_flag=wireshark_flag, workout_id=workout_id)


@wireshark_bp.route("/login/<workout_id>", methods=["GET", "POST"])
def do_admin_login(workout_id):
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return redirect(url_for('wireshark_bp.home', workout_id=workout_id))


@wireshark_bp.route("/logout/<workout_id>", methods=["GET", "POST"])
def admin_logout(workout_id):
    session['logged_in'] = False
    return redirect(url_for('wireshark_bp.home', workout_id=workout_id))
