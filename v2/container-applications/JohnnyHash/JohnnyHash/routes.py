from flask import Blueprint, jsonify, make_response, request, redirect, render_template, url_for, abort
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes
from app_utilities.crypto_suite.hashes import Hashes, HashErrors

johnnyhash = Blueprint(
    'johnnyhash', __name__,
    url_prefix='/johnnyhash',
    template_folder='./templates',
    static_folder='./static'
)


@johnnyhash.route('/HashItOut/<build_id>', methods=['GET', 'POST'])
def hash_it_out(build_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        password_hash = ''
        if workout.get('escape_room', None):
            for puzzle in workout['escape_room']['puzzles']:
                if puzzle['entry_name'] == 'Johnny Hash':
                    password_hash = puzzle['question']
                    break
        elif workout.get('assessment', None):
            password_hash = workout['assessment']['questions'][0]['question']
        if request.method == 'GET':
            return render_template('hashitout.html', pass_hash=password_hash, build_id=build_id)
        elif request.method == 'POST':
            if 'password_file' not in request.files:
                return render_template(
                    'hashitout.html', upload_error=HashErrors.NO_FILE_SUBMITTED,
                    pass_hash=password_hash, build_id=build_id
                )
            else:
                input_file = request.files['password_file']
                hashes = Hashes().validate_hashes_from_file(input_file)
                if type(hashes) != list:
                    return render_template(
                        'hashitout.html', upload_error=HashErrors.EMPTY_FILE,
                        pass_hash=password_hash, build_id=build_id
                    )
                else:
                    return render_template(
                        'hashitout.html', hashed_passwords=hashes,
                        pass_hash=password_hash, build_id=build_id
                    )


@johnnyhash.route('/hidden/<build_id>', methods=['GET'])
def hidden(build_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        logged_in = request.cookies.get('logged_in', None)
        if logged_in is None or logged_in != 'true':
            return redirect(url_for('johnnyhash.login', build_id=build_id))
        else:
            return render_template('hidden.html', build_id=build_id, user='johnny')
    else:
        return redirect('/invalid')


@johnnyhash.route('/login/<build_id>', methods=['GET', 'POST'])
def login(build_id):
    page_template = 'login.html'
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if not workout:
        abort(404)
    else:
        question_id = Hashes().get_question_id(workout)
        if request.method == 'GET':
            return render_template(page_template, build_id=build_id, question_id=question_id)
        elif request.method == 'POST':
            username = request.form.get('username', None)
            password = request.form.get('password', None)
            if username is None or password is None:
                login_error = 'You must submit a username and password'
                return render_template(
                    page_template,
                    login_error=login_error,
                    build_id=build_id,
                    question_id=question_id
                )
            elif question_id:
                valid_password = Hashes().get_password(workout, question_id)
                if username == 'johnny' and password == valid_password:
                    # These are the correct credentials, so the cookie for "logged_in" is set to true
                    Hashes().complete(build_id=build_id, workout_info=workout, question_id=question_id)
                    resp = make_response(redirect(f'/johnnyhash/hidden/{build_id}'))
                    resp.set_cookie('logged_in', 'true')
                    return resp
        login_error = 'Please check your username and password and try again'
        return render_template(
            page_template,
            login_error=login_error,
            build_id=build_id,
            question_id=question_id
        )


@johnnyhash.route('/logout/<build_id>')
def logout(build_id):
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie
    resp = make_response(redirect(f'/johnnyhash/login/{build_id}'))
    resp.set_cookie('logged_in', 'false', expires=0)
    return resp

