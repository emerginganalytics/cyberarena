import binascii
import hashlib
import io
import os
from flask import Blueprint, jsonify, make_response, request, redirect, render_template, url_for
# from globals import ds_client, publish_status

# Initialize Blueprint
johnnyhash = Blueprint(
    'johnnyhash', __name__,
    url_prefix='/johnnyhash',
    template_folder='templates',
    static_folder='static'
)


@johnnyhash.route('/hashing_algorithms/<workout_id>', methods=['GET'])
def hashing_algorithms(workout_id):
    page_template = './hashing_algorithms.jinja'
    return render_template(page_template, workout_id=workout_id,)


@johnnyhash.route('/ajax_calculate_unsalted_hash/<workout_id>', methods=['POST'])
def ajax_calculate_unsalted_hash(workout_id):
    plaintext_password = request.get_json()
    hashed_password = hashlib.sha256(plaintext_password.encode('utf-8')).hexdigest()
    print(hashed_password)
    return jsonify({'hashed_password': hashed_password})


@johnnyhash.route('/ajax_calculate_salted_hash/<workout_id>', methods=['POST'])
def ajax_calculate_salted_hash(workout_id):
    rand_salt = binascii.hexlify(os.urandom(16))
    second_plaintext = request.get_json()
    calculated_hash = hashlib.sha256(second_plaintext.encode('utf-8') + rand_salt).hexdigest()
    salted_hash_password = calculated_hash + ' : ' + rand_salt.decode()
    print(salted_hash_password)
    return jsonify({'salted_hash_password': salted_hash_password})


@johnnyhash.route('/HashItOut/<workout_id>', methods=['GET', 'POST'])
def hash_it_out(workout_id):
    page_template = './hashitout.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    # Only valid workouts should access page
    if workout:
        # Valid workout_id and type:
        if workout['type'] == 'johnnyhash':
            if request.method == 'GET':
                return render_template(
                    page_template,
                    pass_hash=workout['container_info']['correct_password_hash'],
                    workout_id=workout_id
                )
            elif request.method == 'POST':
                if 'password_file' not in request.files:
                    # User did not submit a file.  Show error and let them upload again
                    return render_template(
                        page_template,
                        upload_error="You must choose a file to upload",
                        workout_id=workout_id,
                        pass_hash=workout['container_info']['correct_password_hash']
                    )
                else:
                    # Check to be sure that the user has submitted a file.
                    input_file = request.files['password_file']
                    if input_file.filename == '':
                        # User has submitted a blank file.  Show error and let them upload again.
                        return render_template(
                            page_template,
                            upload_error="You must choose a file to upload",
                            pass_hash=workout['container_info']['correct_password_hash'],
                            workout_id=workout_id,
                        )
                    # At this point, we have a csv file to process
                    raw_input = io.StringIO(input_file.stream.read().decode("UTF8"), newline=None)
                    passwords = raw_input.read().split('\n')
                    hashes = []
                    for password in passwords:
                        hashes.append({
                            'plaintext': password,
                            'hash': hashlib.md5(password.encode('utf-8')).hexdigest()
                        })
                    return render_template(
                        page_template,
                        hashed_passwords=hashes,
                        pass_hash=workout['container_info']['correct_password_hash'],
                        workout_id=workout_id,
                    )
        else:  # Valid workout_id, but not correct workout type
            return redirect(url_for('johnnyhash.invalid'))
    else:  # Workout ID doesn't exist ...
        return redirect(url_for('johnnyhash.invalid'))


@johnnyhash.route('/hidden/<workout_id>')
def hidden(workout_id):
    # This portion sets a cookie with the key "logged_in" to true when a user has authenticated
    # They must be authenticated before viewing this page
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    logged_in = request.cookies.get('logged_in', None)

    if workout:
        if logged_in is None or logged_in != 'true':
            return redirect(url_for('johnnyhash.login', workout_id=workout_id))
        else:
            page_template = './hidden.jinja'
            return render_template(page_template, workout_id=workout_id, user='johnny')
    else:
        return redirect('/invalid')


@johnnyhash.route('/login/<workout_id>', methods=['GET', 'POST'])
def login(workout_id):
    page_template = './login.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    # Check if valid workout and valid workout type
    if not workout:
        return redirect(url_for('johnnyhash.invalid'))
    else:
        if workout['type'] == 'johnnyhash':
            if request.method == 'GET':
                return render_template(page_template, workout_id=workout_id)
            elif request.method == 'POST':
                username = request.form.get('username', None)
                password = request.form.get('password', None)

                print(username, password)
                print(workout['container_info']['correct_password'])
                if username is None or password is None:
                    login_error = 'You must submit a username and password'
                    return render_template(
                        page_template,
                        login_error=login_error,
                        workout_id=workout_id,
                    )
                elif username == 'johnny' and password == workout['container_info']['correct_password']:
                    # These are the correct credentials, so the cookie for "logged_in" is set to true
                    resp = make_response(redirect(f'/johnnyhash/hidden/{workout_id}'))
                    resp.set_cookie('logged_in', 'true')
                    workout_token = workout['assessment']['questions'][0]['key']
                    # app.logger.info(f'Posting Complete to buildthewarrior{dns_suffix}/complete')
                    publish_status(workout_id, workout_token)
                    return resp
                else:
                    login_error = 'Please check your username and password and try again'
                    return render_template(
                        page_template,
                        login_error=login_error,
                        workout_id=workout_id,
                    )
        else:
            return redirect(url_for('johnnyhash.invalid'))


@johnnyhash.route('/logout/<workout_id>')
def logout(workout_id):
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie

    resp = make_response(redirect(f'/johnnyhash/login/{workout_id}'))
    resp.set_cookie('logged_in', 'false', expires=0)

    return resp


@johnnyhash.route('/invalid', methods=['GET'])
def invalid():
    template = './invalid_workout.html'
    return render_template(template)
