from flask import Blueprint, jsonify, redirect, request, render_template
from globals import ds_client
from JohnnyArena.ArenaCiphers import Decoder

# level_2: /cipher-warehouse
# level_3: TBD
# level_4: TBD
arena = Blueprint(
    'arena',
    __name__,
    url_prefix='/arena',
    template_folder='templates/johnnyarena',
    static_folder='static',
)


@arena.route('/<workout_id>', methods=['GET'])
def arena_base(workout_id):
    page_template = 'johnnyarena/johnny-arena-landing.jinja'

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'Trojan Arena Level 2':
            return redirect(f'/cipher-warehouse/{workout_id}')
    else:
        return redirect('/invalid')


# level 2 arena routes
@arena.route('/cipher-warehouse/<workout_id>', methods=['GET', 'POST'])
def cipher_warehouse(workout_id):
    page_template = 'johnnyarena/arena-cipher-warehouse.jinja'

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout:
        if workout['type'] == 'Trojan Arena Level 2':
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')


@arena.route('/cipher-warehouse/cipher-info/<workout_id>', methods=['GET'])
def cipher_info(workout_id):
    page_template = 'johnnyarena/arena-cipher-info.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'Trojan Arena Level 2':
            return render_template(page_template, workout_id=workout_id)
    else:
        return redirect('/invalid')


@arena.route('/ajax_calculate_arena_plaintext', methods=['POST'])
def calculate_plaintext():
    encrypted_message = request.get_json()
    cipher_type = str(encrypted_message['cipher_type'])
    message = str(encrypted_message['ciphertext'])
    cipher_key = encrypted_message['key']
    keyword = encrypted_message['keyword']

    plaintext = str(Decoder(encryption=cipher_type, message=message, key=cipher_key, keyword=keyword))
    return jsonify({'plaintext': plaintext})


# global
@arena.route('/invalid', methods=['GET'])
def invalid():
    template = '/johnnyarena/invalid_workout.html'
    return render_template(template)
