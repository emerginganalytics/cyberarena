import os
from flask import abort, Flask, redirect
from globals import ds_client

# Import App Blueprints
from GenCyberIoT.routes import iot_bp
from GenCyberIoTArena.routes import iot_arena_bp
from NSAHealthcare.routes import iot_nsa_bp

# Register blueprints
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.register_blueprint(iot_bp)
app.register_blueprint(iot_arena_bp)
app.register_blueprint(iot_nsa_bp)


@app.route('/<workout_id>')
def loader(workout_id):
    # Main route; Determines which route to use based off of workout_id
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    """
    Defines valid URLs based on workout type
    Workout types is determined by workout YAML filename
    """
    valid_types = {
        'iot': '/iot',
        'GenCyber Arena': '/iot_arena',
        'nsa-iot': '/healthcare',
    }

    # If workout is valid check for type in URL dict and redirect to value
    if workout:
        workout_type = workout['type']
        if workout_type in valid_types:
            """
            Since all route specific logic is handled at the blueprint level, we only need to
            redirect to the workout specific blueprint app
            """
            return redirect(valid_types[workout_type])
    else:
        return abort(404)


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=4000)
    app.run()
