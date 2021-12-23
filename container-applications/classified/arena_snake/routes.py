import cryptocode
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from globals import ds_client, publish_status

# Blueprint Configuration
arena_snake_bp = Blueprint(
    'arena_snake_bp', __name__,
    url_prefix='/arena_snake',
    template_folder='templates',
    static_folder='static'
)


@arena_snake_bp.route('/<workout_id>', methods=['GET', 'POST'])
def arena_snake(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'arena_snake':
        page_template = 'arena_snake.html'
        completion = False
        return render_template(page_template, workout_id=workout_id, completion=completion)
    else:
        return redirect(404)


@arena_snake_bp.route('/snake_flag/<workout_id>', methods=['POST'])
def snake_flag(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if request.method == 'POST':
        score = (request.json['score'])
        decrypt_key = workout['assessment']['key']
        encrypted_flag = 'KJnLMnsUnLCd/ND3eeJwWPINTzvXTKiiYoNkmjCwbng=*xzz+f0pzhaBX41kaZH3GQg==*+JgHfNlMoOsd7GlTXGqW' \
                         'Fw==*djY9r0Kb0hQb0B7cNZOr4A=='
        flag = cryptocode.decrypt(encrypted_flag, decrypt_key)
        flag_data = {'flag': str(flag)}
        return jsonify(flag_data)


@arena_snake_bp.route('/check_flag/<workout_id>', methods=['POST'])
def check_flag(workout_id):
    page_template = 'arena_snake.html'

    if request.method == 'POST':
        key = ds_client.key('cybergym-workout', workout_id)
        workout = ds_client.get(key)
        workout_token = workout['assessment']['questions'][0]['key']
        if request.form.get('check_button'):
            decrypt_key = workout['assessment']['key']
            encrypted_flag = 'KJnLMnsUnLCd/ND3eeJwWPINTzvXTKiiYoNkmjCwbng=*xzz+f0pzhaBX41kaZH3GQg==*+JgHfNlMoOsd7GlTXGqW' \
                             'Fw==*djY9r0Kb0hQb0B7cNZOr4A=='
            classified_flag = cryptocode.decrypt(encrypted_flag, decrypt_key)
            if classified_flag == request.form['classified_flag']:
                publish_status(workout_id, workout_token)
                completion = True
                return render_template(page_template, workout_id=workout_id, completion=completion)
            else:
                return render_template(page_template, workout_id=workout_id)
