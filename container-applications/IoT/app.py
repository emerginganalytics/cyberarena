import os
from flask import abort, Flask, redirect
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes
# Import App Blueprints
from GenCyberIoT.routes import iot_bp
# from NSAHealthcare.routes import iot_nsa_bp

# Register blueprints
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.register_blueprint(iot_bp)
# app.register_blueprint(iot_nsa_bp)


@app.route('/<workout_id>')
def loader(workout_id):
    # Main route; Determines which route to use based off of workout_id
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id).get()

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
        web_applications = workout.get('web_applications', None)
        if web_applications:
            for ctn in web_applications:
                if ctn['name'] == 'GenCyber IoT':
                    endpoint = ctn.get('starting_directory', 'iot')
        else:
            return redirect(valid_types['iot'])
    else:
        return abort(404)


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=4000)
    app.run()
