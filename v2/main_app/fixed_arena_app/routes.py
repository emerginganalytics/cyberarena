import json
from flask import Blueprint, redirect, render_template, request, session
from utilities.gcp.bucket_manager import BucketManager
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import DatastoreKeyTypes


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
    standard_workout_opt = BucketManager().get_workouts()
    # TODO: Store attack spec in Datastore
    attack_yaml = DataStoreManager().get_attack_specs()

    # TODO: Get Network build specs from stored Datastore object
    # TODO: Get current network build from stored Datastore object
    # This is all the possible variation of quick builds templates that are available
    network_builds = [{'name': 'Access Control', 'id': 'access_control'},
                      {'name': 'Logging', 'id': 'logging'},
                      {'name': 'Firewall', 'id': 'firewall'},
                      {'name': 'Full Build', 'id': 'full'}]

    # Get List of Servers available to for Fixed Network
    fixed_arena = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value, key_id='cln-stoc').get()
    server_list = list(fixed_arena['servers'])

    workouts = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT.value, key_id='cln-stoc').get()

    # TODO: Get list of workstations available for fixed network
    # Render template
    return render_template('fixed_arena_home.html', auth_config=auth_config, attack_spec=attack_yaml,
                           workout_titles=standard_workout_opt, network_builds=network_builds,
                           server_list=server_list, fixed_workout_list=server_list, workstations=None,
                           workouts=workouts)


@fixed_arena_app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    # TODO: It is possible that this handle is redundant and that all logic can be handled in the
    # fixed-arena/home page instead
    auth_config = CloudEnv().auth_config
    build_types = ['build_1', 'build_2', 'build_3']
    if request.method == 'POST':
        # TODO: Future POST requests will be handled by fixed-arena api instead
        print(request.form)
        redirect('/fixed-arena/home')
    return render_template('create_class.html', auth_config=auth_config, build_types=build_types)

