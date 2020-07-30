from app import app
from ArenaCiphers import Decoder
from caesarcipher import CaesarCipher
from flask import redirect, request, render_template, jsonify, make_response
from server_scripts import publish_status, gen_pass, ds_client, set_ciphers, check_caesar

import binascii
import hashlib
import io
import os


@app.route('/<workout_id>')
def home(workout_id):
    page_template = 'pages/home.jinja'
    return render_template(page_template, workout_id=workout_id)


# Generates values based on workout
@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'johnnycipher':
            if workout['container_info']['cipher_one']['cipher'] == '':
                set_ciphers(workout_id)
            return redirect('/caesar/' + workout_id)
        elif workout['type'] == 'johnnyhash':
            if workout['container_info']['correct_password'] == '':
                gen_pass(workout_id)
            return redirect('/md5_page/' + workout_id)
    else:
        return redirect('/invalid')


@app.route('/caesar/<workout_id>', methods=['GET', 'POST'])
def caesar(workout_id):
    page_template = 'pages/cipher.jinja'

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    # Only valid workouts can access
    if workout:
        if workout['type'] == 'johnnycipher':
            firstcipher = workout['container_info']['cipher_one']['cipher']
            secondcipher = workout['container_info']['cipher_two']['cipher']
            thirdcipher = workout['container_info']['cipher_three']['cipher']

            if request.method == 'GET':
                return render_template(
                    page_template,
                    workout_id=workout_id,
                    firstcipher=firstcipher,
                    secondcipher=secondcipher,
                    thirdcipher=thirdcipher,
                )
            elif request.method == 'POST':
                plaintext = request.get_json()
                # ['id'] helps determine which cipher is to be evaluated
                data = check_caesar(workout_id, str(plaintext['cipher']), int(plaintext['id']))

                return jsonify({
                    'message1': data['cipher1']['cipher'],
                    'status1':  data['cipher1']['status'],
                    'message2': data['cipher2']['cipher'],
                    'status2':  data['cipher2']['status'],
                    'message3': data['cipher3']['cipher'],
                    'status3':  data['cipher3']['status'],
                })
        else:
            return redirect('/invalid')
    else:
        return redirect('/invalid')


@app.route('/ajax_calculate_caesar/<workout_id>', methods=['POST'])
def ajax_calculate_caesar(workout_id):
    # Returns deciphered message
    encrypted_message = request.get_json()
    key = int(encrypted_message['key'])
    message = str(encrypted_message['ciphertext'])
    plaintext = CaesarCipher(message, offset=key).decoded

    return jsonify({'plaintext': plaintext})


@app.route('/hashing_algorithms/<workout_id>', methods=['GET'])
def hashing_algorithms(workout_id):
    page_template = 'pages/hashing_algorithms.jinja'

    return render_template(page_template, workout_id=workout_id,)


@app.route('/ajax_calculate_unsalted_hash/<workout_id>', methods=['POST'])
def ajax_calculate_unsalted_hash(workout_id):
    plaintext_password = request.get_json()

    hashed_password = hashlib.sha256(plaintext_password.encode('utf-8')).hexdigest()

    print(hashed_password)

    return jsonify({'hashed_password': hashed_password})


@app.route('/ajax_calculate_salted_hash/<workout_id>', methods=['POST'])
def ajax_calculate_salted_hash(workout_id):
    rand_salt = binascii.hexlify(os.urandom(16))

    second_plaintext = request.get_json()

    calculated_hash = hashlib.sha256(second_plaintext.encode('utf-8') + rand_salt).hexdigest()

    salted_hash_password = calculated_hash + ' : ' + rand_salt.decode()

    print(salted_hash_password)

    return jsonify({'salted_hash_password': salted_hash_password})


@app.route('/md5_page/<workout_id>', methods=['GET', 'POST'])
def md5_page(workout_id):
    page_template = 'pages/md5_page.jinja'

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
            return redirect('/invalid')
    else:  # Workout ID doesn't exist ...
        return redirect('/invalid')


@app.route('/hidden/<workout_id>')
def hidden(workout_id):
    # This portion sets a cookie with the key "logged_in" to true when a user has authenticated
    # They must be authenticated before viewing this page
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    logged_in = request.cookies.get('logged_in', None)

    if workout:
        if logged_in is None or logged_in != 'true':
            return redirect('/login/{}'.format(workout_id))
        else:
            page_template = 'pages/hidden.jinja'
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')


@app.route('/login/<workout_id>', methods=['GET', 'POST'])
def login(workout_id):
    page_template = 'pages/login.jinja'

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    # Check if valid workout and valid workout type
    if not workout:
        return redirect('/invalid')
    else:
        if workout['type'] == 'johnnyhash':
            if request.method == 'GET':
                return render_template(page_template, workout_id=workout_id)
            elif request.method == 'POST':
                username = request.form.get('username', None)
                password = request.form.get('password', None)

                print(username, password)

                if username is None or password is None:
                    login_error = 'You must submit a username and password'
                    return render_template(
                        page_template,
                        login_error=login_error,
                        workout_id=workout_id,
                    )
                elif username == 'johnny' and password == workout['container_info']['correct_password']:
                    # These are the correct credentials, so the cookie for "logged_in" is set to true
                    resp = make_response(redirect('/hidden/{}'.format(workout_id)))
                    resp.set_cookie('logged_in', 'true')
                    workout_token = workout['assessment']['questions'][0]['key']
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
            return redirect('/invalid')


@app.route('/logout/<workout_id>')
def logout(workout_id):
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie

    resp = make_response(redirect('/login/{}'.format(workout_id)))
    resp.set_cookie('logged_in', 'false', expires=0)

    return resp


# The Following Routes are used by Arena Workouts Only
@app.route('/arena/landing/<workout_id>', methods=['GET'])
def arena(workout_id):
    page_template = 'pages/johnny-arena-landing.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['name'] == 'Trojan Arena Level 2':
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')


@app.route('/arena/cipher-warehouse/<workout_id>', methods=['GET', 'POST'])
def cipher_warehouse(workout_id):
    page_template = 'pages/arena-cipher-warehouse.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout:
        if workout['name'] == 'Trojan Arena Level 2':
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')

@app.route('/arena/cipher-warehouse/cipher-info/<workout_id>', methods=['GET'])
def cipher_info(workout_id):
    page_template = 'pages/arena-cipher-info.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['name'] == 'Trojan Arena Level 2':
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')

@app.route('/ajax_calculate_arena_plaintext', methods=['POST'])
def calculate_plaintext():
    encrypted_message = request.get_json()
    cipher_type = str(encrypted_message['cipher_type'])
    message = str(encrypted_message['ciphertext'])
    cipher_key = encrypted_message['key']
    keyword = encrypted_message['keyword']

    plaintext = str(Decoder(encryption=cipher_type, message=message, key=cipher_key, keyword=keyword))
    return jsonify({'plaintext': plaintext})


@app.route('/invalid', methods=['GET'])
def invalid():
    template = '/pages/invalid_workout.html'
    return render_template(template)
