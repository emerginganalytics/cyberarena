from flask import Blueprint, jsonify, redirect, request, render_template
from globals import ds_client
from GenCyber1.utils import get_arena_sub_cipher

# Initialize Blueprint
johnnyGenCipher = Blueprint(
    'johnnyGenCipher',
    __name__,
    url_prefix='/johnnyGenCipher',
    template_folder='email_templates/johnnyGenCipher',
    static_folder='static',
)


@johnnyGenCipher.route('/substitution/<workout_id>', methods=['GET'])
def substitution(workout_id):
    page_template = 'johnnyGenCipher/substitution.jinja'
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'GenCyber Arena Level 1':
            if request.method == 'GET':
                cipher = get_arena_sub_cipher()

                return render_template(
                    page_template,
                    workout_id=workout_id,
                    sub_cipher=cipher,
                )
        else:
            return redirect('/invalid')
    else:
        return redirect('/invalid')


@johnnyGenCipher.route('/invalid', methods=['GET'])
def invalid():
    template = 'johnnyGenCipher/invalid_workout.html'
    return render_template(template)
