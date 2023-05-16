""""
JohnnyHash blueprint is a collection of cryptography based workouts from basic password hashing to introduction
to symmetric and asymmetric ciphers
"""
from flask import Blueprint, jsonify, make_response, request, redirect, render_template, url_for, abort
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes
from app_utilities.crypto_suite.hashes import Hashes
from app_utilities.crypto_suite.ciphers import Ciphers

from johnnyhash.utilities import CaesarCipherWorkout

johnnyhash_bp = Blueprint(
    'johnnyhash', __name__,
    url_prefix='/johnnyhash',
    template_folder='./templates',
    static_folder='./static'
)


@johnnyhash_bp.route('/HashItOut/<build_id>', methods=['GET'])
def hash_it_out(build_id):
    logged_in = request.cookies.get('logged_in', None)
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        hashes = Hashes(workout_info=workout, build_id=build_id)
        # Generate and set the hash if needed
        hashes.set_md5_hash()
        # Get the assessment object from the workout
        assessment = hashes.get_assessment()
        password_hash = assessment['question']
        hash_api = url_for('hashes')
        return render_template('hashitout-v2.html', pass_hash=password_hash, build_id=build_id,
                               hashed_passwords=[], hash_api=hash_api, logged_in=logged_in)
    return redirect('/invalid')


@johnnyhash_bp.route('/tefference/<build_id>', methods=['GET'])
def tefference(build_id):
    logged_in = request.cookies.get('logged_in', None)
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        hashes = Hashes(workout_info=workout, build_id=build_id)
        # Generate and set the hash if needed
        hashes.set_md5_hash()
        # Get the assessment object from the workout
        assessment = hashes.get_assessment()
        password_hash = assessment['question']
        hash_api = url_for('hashes')
        return render_template('tefference-v2.html', pass_hash=password_hash, build_id=build_id,
                               hashed_passwords=[], hash_api=hash_api, logged_in=logged_in)
    return redirect('/invalid')


@johnnyhash_bp.route('/hidden/<build_id>', methods=['GET'])
def hidden(build_id):
    logged_in = request.cookies.get('logged_in', None)
    if logged_in is None or logged_in != 'true':
        return redirect(url_for('johnnyhash.hash_it_out', build_id=build_id))
    else:
        workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
        if workout:
            if 'escape_room' in workout:
                user = 'mart1n56'
            else:
                user = 'johnny'
            return render_template('hidden-v2.html', build_id=build_id, user=user)
        else:
            return redirect('/invalid')


@johnnyhash_bp.route('/login/<build_id>', methods=['POST'])
def login(build_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        assessment = Hashes(workout_info=workout, build_id=build_id).get_assessment()
        question_id = assessment['id']
        if request.method == 'POST':
            login_error = 'Missing Required Fields'
            username = request.form.get('username', None)
            password = request.form.get('password', None)
            invalid = ['', None]
            if (username or password) in invalid:
                login_error = 'You must submit a username and password'
            else:
                if question_id:
                    hashes = Hashes(workout_info=workout, build_id=build_id)
                    valid_password = hashes.get_password()
                    if (username == 'johnny' or username == 'mart1n56') and password == valid_password:
                        # These are the correct credentials, so the cookie for "logged_in" is set to true
                        hashes.complete(question_id=question_id)
                        resp = make_response(redirect(url_for('johnnyhash.hidden', build_id=build_id)))
                        resp.set_cookie('logged_in', 'true')
                        return resp
                    login_error = 'Please check your username and password and try again'
            return jsonify({'status': 400, 'data': '400: Bad Request', 'error_msg': login_error})
    return jsonify({'status': 404, 'data': 'Not Found', 'error_msg': 'Not Found'})


@johnnyhash_bp.route('/logout/<build_id>')
def logout(build_id):
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie
    resp = make_response(redirect(url_for('johnnyhash.hash_it_out', build_id=build_id)))
    resp.set_cookie('logged_in', 'false', expires=0)
    return resp


@johnnyhash_bp.route('/ciphers/<build_id>', methods=['GET'])
def ciphers(build_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id).get()
    if workout:
        ops = Ciphers.options()
        if populated := CaesarCipherWorkout(build_id=build_id, build=workout).set():
            assessment = populated.get('assessment', None)
        else:
            assessment = workout.get('assessment', None)
        completed = 0
        for question in assessment['questions']:
            if question['complete']:
                completed += 1
        return render_template('johnnycipher.html', build_id=build_id, workout=workout, ciphers=ops,
                               completed=completed)
    return redirect('/invalid')


@johnnyhash_bp.route('/ciphers/cipher-info/<build_id>', methods=['GET'])
def cipher_info(build_id):
    return render_template('cipher_info.html', build_id=build_id)


def _get_assessment(build):
    if escape_room := build.get('escape_room', None):
        return build['escape_room']['puzzles']
    else:
        return build['assessment']['questions']
