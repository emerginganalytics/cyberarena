import base64
import onetimepass
import os
from flask import Flask, redirect, abort, jsonify, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

# App imports
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.globals import DatastoreKeyTypes
from app_utilities.crypto_suite.hashes import Hashes

# App Blueprint Imports
from johnnyhash.routes import johnnyhash_bp


# API Views
from api.johnnyhash_api import JohnnyHashAPI, JohnnyCipherAPI

cloud_env = CloudEnv()

# --------------------------- FLASK APP --------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'
app.jinja_env.globals['project'] = cloud_env.project
bootstrap = Bootstrap(app)

# db Config
db = SQLAlchemy(app)
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register Blueprints
app.register_blueprint(johnnyhash_bp)


@app.route('/<build_id>')
def home(build_id):
    build = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if build:
        web_app = build.get('web_applications', None)
        if web_app:
            directory = web_app[0].get('starting_directory', None)
            if directory:
                return redirect(directory)
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
register_api(view=JohnnyCipherAPI, endpoint='ciphers', url='/api/ciphers', pk='build_id')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
