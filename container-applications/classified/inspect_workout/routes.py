import cryptocode
from flask import Blueprint, render_template, redirect, request, url_for
from globals import ds_client, publish_status

# Blueprint Configuration
inspect_bp = Blueprint(
    'inspect_bp', __name__,
    url_prefix='/inspect',
    template_folder='templates',
    static_folder='static'
)


@inspect_bp.route('/<workout_id>')
def inspect(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'inspect':
        page_template = 'inspect.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@inspect_bp.route('/xsfiedSTRflag/<workout_id>', methods=['GET', 'POST'])
def xsfiedSTRflag(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'inspect':
        page_template = 'index.html'
        return render_template(page_template, workout_id=workout_id)
    else:
        return redirect(404)


@inspect_bp.route('/login/<workout_id>', methods=['POST'])
def login(workout_id):
    page_template = 'inspect.html'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'inspect':
        if request.method == 'POST':
            if request.form['password'] == 'TrojanSpirit!2021' and request.form['username'] == 'Maximus':
                decrypt_key = workout['assessment']['key']
                classified_flag = 'gecJuFQuv1FhQAfLDvn9f6j6xu/GACm00wqyoWVKUJQ=*gXSP1UFZELV59Qz6yP0Y+w==*' \
                                  'y6cg3ujMtm7eSklW2SX3JQ==*C4GDYpzjfozIsTQWVuUc4A=='
                plaintext_flag = cryptocode.decrypt(classified_flag, decrypt_key)
                return render_template(page_template, workout_id=workout_id, classified_flag=plaintext_flag)
            else:
                return redirect(url_for('inspect_bp.xsfiedSTRflag   ', workout_id=workout_id))
    else:
        return redirect(404)


@inspect_bp.route('/check_flag/<workout_id>', methods=['POST'])
def check_flag(workout_id):
    if request.method == 'POST':
        key = ds_client.key('cybergym-workout', workout_id)
        page_template = 'inspect.html'
        workout = ds_client.get(key)
        workout_token = workout['assessment']['questions'][0]['key']

        if request.form.get('check_button'):
            decrypt_key = workout['assessment']['key']
            encrypted_flag = 'gecJuFQuv1FhQAfLDvn9f6j6xu/GACm00wqyoWVKUJQ=*gXSP1UFZELV59Qz6yP0Y+w==*' \
                              'y6cg3ujMtm7eSklW2SX3JQ==*C4GDYpzjfozIsTQWVuUc4A=='
            classified_flag = cryptocode.decrypt(encrypted_flag, decrypt_key)
            if classified_flag == request.form['classified_flag']:
                publish_status(workout_id, workout_token)
                completion = True
                return render_template(page_template, workout_id=workout_id, completion=completion)
            else:
                return render_template(page_template, workout_id=workout_id)
