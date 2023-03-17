import json
import flask
import requests
from flask import abort, Blueprint, redirect, render_template, request, session
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, BuildConstants


fixed_arena_app = Blueprint('fixed_arena', __name__, url_prefix="/fixed-arena",
                        static_folder="./static", template_folder="./templates")
cloud_env = CloudEnv()


@fixed_arena_app.route('/', methods=['GET'])
def base():
    return redirect("/fixed-arena/home")


@fixed_arena_app.route("/home", methods=['GET'])
def home():
    """
    Kind id parent_id build_type
    Workspaces are denoted by fixed-arena-workout.workspace_servers
    :return:
    """
    auth_config = cloud_env.auth_config
    # Get built fixed-arenas for project
    fixed_arenas_query = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA.value).query()
    fixed_arenas = list(fixed_arenas_query.fetch())

    # Get fixed-arena workspaces
    workspaces = []
    # Get fixed-arena and fixed-arena class spec names
    bm = BucketManager(env_dict=cloud_env.get_env())
    class_specs = bm.get_class_list()
    fixed_arena_specs = bm.get_fixed_arena_list()

    # Render template
    return render_template('fixed_arena_home.html', auth_config=auth_config, fixed_arenas=fixed_arenas,
                           workspaces=workspaces, class_spec_list=class_specs, fixed_arena_spec_list=fixed_arena_specs)


@fixed_arena_app.route('/class/<build_id>', methods=['GET'])
def class_landing(build_id):
    auth_config = cloud_env.auth_config
    attack_spec_query = DataStoreManager(key_id=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC).query()
    attack_specs = list(attack_spec_query.fetch())
    fa_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value, key_id=build_id).get()
    if fa_class:
        workspaces = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                                     parent_id=fa_class.key.name)
        return render_template('fixed_arena_class.html', auth_config=auth_config, fixed_arena_class=fa_class,
                               workspaces=workspaces, attack_spec=attack_specs, main_app_url=cloud_env.main_app_url)
    abort(404)

