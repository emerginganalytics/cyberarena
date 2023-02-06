import os
from flask import Flask, redirect, abort, jsonify, render_template, request, session
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.globals import DatastoreKeyTypes
from app_utilities.crypto_suite.hashes import Hashes

# App Blueprints
from JohnnyHash.routes import johnnyhash

# API Views
from api.johnnyhash_api import JohnnyHashAPI

# --------------------------- FLASK APP --------------------------
app = Flask(__name__)
app.register_blueprint(johnnyhash)
app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'
app.jinja_env.globals['project'] = CloudEnv().project


# Loader Route; Used to determine which Blueprint to use
@app.route('/<build_id>')
def loader(build_id):
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout:
        if workout.get('escape_room', None):
            Hashes(build_id).set_md5_hash()
            return redirect(f'/johnnyhash/HashItOut/{build_id}')
    return redirect('/invalid')


@app.route('/invalid', methods=['GET'])
def invalid():
    return render_template('invalid_workout.html')


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule(f'{url}<{pk_type}:{pk}>', view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])


# Register API Routes
register_api(view=JohnnyHashAPI, endpoint='hashes', url='/api/hashes', pk='build_id')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
