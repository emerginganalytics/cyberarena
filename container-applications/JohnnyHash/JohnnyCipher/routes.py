from Ciphers.caesarcipher import CaesarCipher
from flask import Blueprint, jsonify, redirect, request, render_template, url_for
from globals import ds_client
from JohnnyCipher.utils import CaesarCipherBuilder, SubstitutionCipherBuilder

# Initialize Blueprint
johnnycipher = Blueprint(
    'johnnycipher',
    __name__,
    url_prefix='/johnnycipher',
    template_folder='email_templates',
    static_folder='static',
)


@johnnycipher.route('/caesar/<workout_id>', methods=['GET', 'POST'])
def caesar(workout_id):
    page_template = './cipher.jinja'

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
                # app.logger.info('Checking cipher with id : %d' % int(plaintext['id']))
                validator = CaesarCipherBuilder(workout_id)
                data = validator.check_caesar(str(plaintext['cipher']), int(plaintext['id']))

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


@johnnycipher.route('/ajax_calculate_caesar/<workout_id>', methods=['POST'])
def ajax_calculate_caesar(workout_id):
    # Returns deciphered message
    encrypted_message = request.get_json()
    key = int(encrypted_message['key'])
    message = str(encrypted_message['ciphertext'])
    plaintext = CaesarCipher(message, offset=key).decoded

    return jsonify({'plaintext': plaintext})


@johnnycipher.route('/substitution/<workout_id>', methods=['GET', 'POST'])
def substitution(workout_id):
    page_template = './substitution.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'johnnycipher':
            if request.method == 'GET':
                cipher = workout['container_info']['sub_cipher']['cipher']
                status = workout['assessment']['questions'][3]['complete']

                return render_template(
                    page_template,
                    workout_id=workout_id,
                    sub_cipher=cipher,
                    status=status
                )
            elif request.method == 'POST':
                submission = request.get_json()
                validator = SubstitutionCipherBuilder(workout_id=workout_id)
                check_sub = validator.check_sub_cipher(submission['cipher'])
                cipher = check_sub['message']
                status = check_sub['status']

                return jsonify({'message': cipher, 'status': status})
        else:
            return redirect(url_for('johnnycipher.invalid'))
    else:
        return redirect(url_for('johnnycipher.invalid'))


@johnnycipher.route('/invalid', methods=['GET'])
def invalid():
    template = 'email_templates/invalid_workout.html'
    return render_template(template)
