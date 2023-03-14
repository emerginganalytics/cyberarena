"""
Contains collection of web-based vulnerability workouts:
- xss : /xss/xss_d/<wid>
- 2fa : /tfh/<wid>
- sql injection :  /sql_injection/<wid>
- inspect : /inspect/<wid>
- arena snake : /arena_snake/<wid>
- wireshark : /wireshark/<wid>
"""
import cryptocode
from flask import abort, Blueprint, flash, g, jsonify, make_response, request, redirect, render_template, session, url_for
from flask import current_app as app
from flask_bootstrap import Bootstrap
from io import BytesIO

# app imports
from classified.databases import SQLInjection, XSS, RegisterForm, LoginForm
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes

classified_bp = Blueprint(
    'classified', __name__,
    url_prefix='/classified',
    template_folder='./templates',
    static_folder='./static',
)

# Arena Snake Routes


# Inspect Routes
@classified_bp.route('/inspect/<workout_id>')
def inspect(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        return render_template('inspect.html', workout_id=workout_id)
    return redirect(404)


@classified_bp.route('/inspect/xsfiedSTRflag/<workout_id>', methods=['GET', 'POST'])
def xsfiedSTRflag(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        return render_template('inspect_index.html', workout_id=workout_id)
    return redirect(404)


@classified_bp.route('/inspect/login/<workout_id>', methods=['GET', 'POST'])
def inspect_login(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        if request.method == 'POST':
            if request.form['password'] == 'TrojanSpirit!2021' and request.form['username'] == 'Maximus':
                decrypt_key = workout['assessment']['questions'][0]['id']
                classified_flag = 'gecJuFQuv1FhQAfLDvn9f6j6xu/GACm00wqyoWVKUJQ=*gXSP1UFZELV59Qz6yP0Y+w==*' \
                                  'y6cg3ujMtm7eSklW2SX3JQ==*C4GDYpzjfozIsTQWVuUc4A=='
                plaintext_flag = cryptocode.decrypt(classified_flag, decrypt_key)
                return render_template('inspect.html', workout_id=workout_id, classified_flag=plaintext_flag)
            else:
                return redirect(url_for('classified_bp.xsfiedSTRflag', workout_id=workout_id))
    return redirect(404)




# SQL Injection Routes
@classified_bp.route('/sql-injection/<workout_id>')
def sql_injection(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        return render_template('sql_index.html', workout_id=workout_id)
    return redirect(404)


@classified_bp.route('/sql-injection/login/<workout_id>', methods=['POST'])
def sql_login(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        sql = SQLInjection()
        # Get login form data and attempt login
        uname, pwd = (request.json['username'], request.json['password'])
        g.db = sql.connect()
        cur = g.db.execute("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %
                           (uname, sql._hash_pass(pwd)))
        # Credentials exist, decrypt and return flag
        if cur.fetchone():
            decrypt_key = workout['assessment']['questions'][0]['id']
            encr_flag = "z3iMRhodBpfpOPQalsurIEQmbjpv52PYL0HDnqxCVyu+aQCVTRPWBNv6QI8U*fQKWPyfP5gtUExz5MnLuWg==" \
                        "*5j/Up6s28F82Am+O7HTfHQ==*M2pIUrpUwaAXlc4ohBKpxQ=="
            flag = cryptocode.decrypt(encr_flag, decrypt_key)
            result = {'status': 'success',
                      'flag': flag}
        else:
            result = {'status': 'fail'}
        g.db.close()
        return jsonify(result)


@classified_bp.route('/sql-injection/check_flag/<workout_id>', methods=['POST'])
def check_sql_flag(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        if request.form.get('check_button'):
            decrypt_key = workout['assessment']['questions'][0]['id']
            encr_flag = "z3iMRhodBpfpOPQalsurIEQmbjpv52PYL0HDnqxCVyu+aQCVTRPWBNv6QI8U*fQKWPyfP5gtUExz5MnLuWg==" \
                        "*5j/Up6s28F82Am+O7HTfHQ==*M2pIUrpUwaAXlc4ohBKpxQ=="
            classified_flag = cryptocode.decrypt(encr_flag, decrypt_key)
            if classified_flag == request.form['classified_flag']:
                workout['assessment']['questions'][0]['complete'] = True
                DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).put(workout)
                completion = True
                return render_template('sql_index.html', workout_id=workout_id, completion=completion)
            else:
                return render_template('sql_index.html', workout_id=workout_id)


# Wireshark Routes
@classified_bp.route('/wireshark/<workout_id>')    
def wireshark_home(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        if not session.get('logged_in'):
            return render_template('wireshark_index.html', workout_id=workout_id)
        else:
            decrypt_key = workout['assessment']['questions'][0]['id']
            encrypted_flag = 'w7w1HZQSOlQk7cxRjqICoIXkFbUsjnr9CHJkvZ51Iw==*9o+WrK5lFOZG70IARQ5HGA==*7bLeQoMR/IhXQjlvey' \
                             '71KQ==*D+iRjmWUsHXkKTC+G6cF4g=='
            wireshark_flag = cryptocode.decrypt(encrypted_flag, decrypt_key)
            return render_template('wireshark_flag.html', wireshark_flag=wireshark_flag, workout_id=workout_id)


@classified_bp.route('/wireshark/login/<workout_id>', methods=['GET', 'POST'])
def do_admin_login(workout_id):
    if request.form['psw'] == 'cyberSecret42' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Incorrect Password')
    return redirect(url_for('classified_bp.wireshark_home', workout_id=workout_id))


@classified_bp.route('/wireshark/logout/<workout_id>', methods=['GET', 'POST'])
def admin_logout(workout_id):
    session['logged_in'] = False
    return redirect(url_for('wireshark_bp.home', workout_id=workout_id))


# XSS Routes
@classified_bp.route('/xss/dom/<workout_id>', methods=['GET', 'POST'])
def xss_d(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        name = 'Stranger'
        bad_request = 'bad request'
        if request.args.get('bad_request'):
            bad_request = request.args.get('bad_request')
        return render_template('xss_dom.html', name=name, bad_request=bad_request, workout_id=workout_id)
    return redirect(404)


@classified_bp.route('/xss/reflected/<workout_id>', methods=['GET', 'POST'])
def xss_r(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        name = 'Stranger'
        if request.method == 'POST':
            name = request.form['name']
        return render_template('xss_r.html', name=name, workout_id=workout_id)
    return redirect(404)


@classified_bp.route('/xss/stored/<workout_id>', methods=['GET', 'POST'])
def xss_s(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        xss = XSS()
        if request.method == 'POST':
            xss.add_feedback(request.form['feedback'], workout_id)
        search_query = request.args.get('query')
        feedbacks = xss.get_feedback(workout_id, search_query)
        return render_template('xss_s.html', feedbacks=feedbacks, search_query=search_query, workout_id=workout_id)
    return redirect(404)


# Error Handlers
@classified_bp.errorhandler(404)
def page_not_found_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


@classified_bp.errorhandler(500)
def internal_server_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


