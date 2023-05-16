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
import re
from flask import abort, Blueprint, flash, g, jsonify, make_response, request, redirect, render_template, session, url_for
from flask import current_app as app
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
@classified_bp.route('/snake/<workout_id>')
def snake(workout_id):
    pass


# Inspect Routes
@classified_bp.route('/inspect/<workout_id>')
def inspect(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        completed = workout['assessment']['questions'][0].get('complete', False)
        if completed:
            flag = workout['assessment']['questions'][0].get('answer', None)
            return render_template('inspect-v2.html', workout=workout, completed=completed,
                                   classified_flag=flag)
        return render_template('inspect-v2.html', workout=workout, completed=completed)
    return abort(404)


@classified_bp.route('/inspect/login/<workout_id>', methods=['POST'])
def inspect_login(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        if request.method == 'POST':
            assessment = workout['assessment']['questions']
            encrypted = 'e8OuZsMdvUAj167q1w+1j+w=*/+mCoSMHVdMmVDdyjoxR2Q==*9Jvf3hi2x4n29712s/Z3Dw==*tVukPNKaq9+Gr+dFRgldNQ=='
            password = cryptocode.decrypt(encrypted, password=assessment['key'])
            if request.form['password'] == password and request.form['username'] == 'Maximus':
                completed = True
                classified_flag = assessment[0]['answer']
                assessment['complete'] = True
                DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).put(workout)
                resp = make_response(render_template('inspect-v2.html', workout=workout, completed=completed,
                                                     classified_flag=classified_flag))
                resp.set_cookie('AwesomeITUser', 'Maximus')
                return resp
            else:
                completed = False
                return render_template('inspect-v2.html', workout=workout, completed=completed)
        return abort(400)
    return abort(404)


# SQL Injection Routes
@classified_bp.route('/sql-injection/<workout_id>')
def sql_injection(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        pass
    return render_template('sql_index.html', workout_id=workout_id)
    # return redirect(404)


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


# XSS Routes
@classified_bp.route('/xss/dom/<workout_id>', methods=['GET', 'POST'])
def dom(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        attack = {}
        name = 'Stranger'
        if bad_request := request.args.get('bad_request', None):
            attack['type'] = 'dom'
            attack['name'] = name
            attack['bad_request'] = bad_request
            attack['cleaned'] = ''.join(re.split('|<script>|, |</script>|', bad_request))
        return render_template('xss_dom.html', attack=attack, workout=workout)
    return abort(404)


@classified_bp.route('/xss/reflected/<workout_id>', methods=['GET', 'POST'])
def reflected(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        attack = {}
        name = 'Stranger'
        form = request.form
        if name := form.get('name', None):
            attack['type'] = 'reflected'
            attack['name'] = name
            attack['cleaned'] = ''.join(re.split('|<script>|, |</script>|', attack['name']))
        return render_template('xss_r.html', attack=attack, workout=workout)
    return abort(404)


@classified_bp.route('/xss/stored/<workout_id>', methods=['GET', 'POST'])
def stored(workout_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()
    if workout:
        xss = XSS()
        attack = {'type': 'stored', 'feedbacks': [], 'cleaned': [], 'search_query': ''}
        if request.method == 'POST':
            if feedback := request.form.get('feedback', None):
                xss.add_feedback(feedback, workout_id)
        if search_query := request.args.get('query', None):
            feedbacks = xss.get_feedback(workout_id, search_query)
            attack['feedbacks'] = feedbacks
            attack['cleaned'] = [''.join(re.split('|<script>|, |</script>|', i)) for i in feedbacks]
            attack['search_query'] = search_query
        return render_template('xss_s.html', attack=attack, workout=workout)
    return abort(404)
