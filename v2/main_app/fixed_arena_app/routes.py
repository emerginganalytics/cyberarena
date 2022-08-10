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


@fixed_arena_app.route('/', methods=['GET'])
def base():
    return redirect("/fixed-arena/home")


@fixed_arena_app.route("/home", methods=['GET'])
def home():
    """
    Kind id parent_id build_type
    fixed-arena-workout, ohzuxkhxee, cln-stoc, fixed_arena_workout

    Kind build_type id
    fixed-arena, fixed_arena, cln-stoc

    Workspaces are denoted by fixed-arena-workout.workspace_servers
    :return:
    """
    auth_config = CloudEnv().auth_config
    # Get built fixed-arenas for project
    fixed_arenas_query = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA.value).query()
    fixed_arenas = list(fixed_arenas_query.fetch())

    # For each fixed-arena, check for any existing classes
    if fixed_arenas:
        for fixed_arena in fixed_arenas:
            fa_class = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA_CLASS.value).query(
                filter_key='parent_id', op='=', value=fixed_arena['id']
            )
            if fa_class:
                fixed_arena['class'] = {'id': fa_class[0]['id'], 'state': fa_class[0]['state']}

            # TODO: Need to return the only current active class if it exists
            '''
            if fa_class:
                for i in fa_class:
                    if i['state'] == BuildConstants.FixedArenaClassStates.RUNNING.value:
                        fixed_arena['class'] = {'id': i['id'], 'state': i['state']}
            '''
    # Get fixed-arena workspaces
    workspaces = []
    # Get fixed-arena and fixed-arena class spec names
    bm = BucketManager()
    class_specs = bm.get_class_list()
    fixed_arena_specs = bm.get_fixed_arena_list()

    # Render template
    return render_template('fixed_arena_home.html', auth_config=auth_config, fixed_arenas=fixed_arenas,
                           workspaces=workspaces, class_spec_list=class_specs, fixed_arena_spec_list=fixed_arena_specs)


@fixed_arena_app.route('/class/<build_id>', methods=['GET'])
def class_landing(build_id):
    auth_config = CloudEnv().auth_config
    # TODO: Store/Get attack specs in/from Datastore
    attack_yaml = DataStoreManager().get_attack_specs()
    fa_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value, key_id=build_id).get()
    if fa_class:
        workspace_query = DataStoreManager(key_id=DatastoreKeyTypes.CYBERGYM_WORKOUT.value).query()
        workspace_query.add_filter('parent_id', '=', fa_class.key.name)
        workspace_query.add_filter('parent_build_type', '=', 'fixed_arena_class')
        workspaces = list(workspace_query.fetch())

        return render_template('fixed_arena_class.html', auth_config=auth_config, fixed_arena_class=fa_class,
                               workspaces=workspaces, attack_spec=attack_yaml)
    abort(404)
