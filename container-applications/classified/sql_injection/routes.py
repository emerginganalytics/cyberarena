import cryptocode
from flask import Blueprint, g, jsonify, redirect, request, render_template
from globals import ds_client, publish_status
from sql_injection.config import *

# Blueprint Configuration
sql_injection_bp = Blueprint(
    'sql_injection_bp', __name__,
    url_prefix='/sql_injection',
    template_folder='email_templates',
    static_folder='static'
)


@sql_injection_bp.route('/<workout_id>')
def sql_injection(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'sql_injection':
        page_template = 'sql_index.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@sql_injection_bp.route('/login_SQL/<workout_id>', methods=['POST'])
def login_sql(workout_id):
    if request.method == 'POST':
        key = ds_client.key('cybergym-workout', workout_id)
        workout = ds_client.get(key)

        # Get login form data and attempt login
        uname, pword = (request.json['username'], request.json['password'])
        g.db = connect_db()
        cur = g.db.execute("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %
                           (uname, hash_pass(pword)))
        # Credentials exist, decrypt and return flag
        if cur.fetchone():
            decrypt_key = workout['assessment']['key']
            encr_flag = "z3iMRhodBpfpOPQalsurIEQmbjpv52PYL0HDnqxCVyu+aQCVTRPWBNv6QI8U*fQKWPyfP5gtUExz5MnLuWg==" \
                        "*5j/Up6s28F82Am+O7HTfHQ==*M2pIUrpUwaAXlc4ohBKpxQ=="
            flag = cryptocode.decrypt(encr_flag, decrypt_key)
            result = {'status': 'success',
                      'flag': flag}
        else:
            result = {'status': 'fail'}
        g.db.close()
        return jsonify(result)


@sql_injection_bp.route('/check_flag/<workout_id>', methods=['POST'])
def check_flag(workout_id):
    if request.method == 'POST':
        key = ds_client.key('cybergym-workout', workout_id)
        page_template = 'sql_index.html'
        workout = ds_client.get(key)
        workout_token = workout['assessment']['questions'][0]['key']
        if request.form.get('check_button'):
            decrypt_key = workout['assessment']['key']
            encr_flag = "z3iMRhodBpfpOPQalsurIEQmbjpv52PYL0HDnqxCVyu+aQCVTRPWBNv6QI8U*fQKWPyfP5gtUExz5MnLuWg==" \
                        "*5j/Up6s28F82Am+O7HTfHQ==*M2pIUrpUwaAXlc4ohBKpxQ=="
            classified_flag = cryptocode.decrypt(encr_flag, decrypt_key)
            if classified_flag == request.form['classified_flag']:
                publish_status(workout_id, workout_token)
                completion = True
                return render_template(page_template, workout_id=workout_id, completion=completion)
            else:
                return render_template(page_template, workout_id=workout_id)
