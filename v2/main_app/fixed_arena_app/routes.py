import json
import flask
import requests
from flask import abort, Blueprint, redirect, render_template, request, session
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, BuildConstants
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer


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
    if user_email := session.get('user_email', None):
        auth = ArenaAuthorizer()
        if user := auth.authorized(email=user_email, base=auth.UserGroups.INSTRUCTOR):
            auth_config = cloud_env.auth_config
            # Get built fixed-arenas for project
            fixed_arenas = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value).query()

            # Get fixed-arena workspaces
            workspaces = []
            # Get fixed-arena and fixed-arena class spec names
            dm = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG)
            class_specs = dm.query(filters=[('build_type', '=', BuildConstants.BuildType.FIXED_ARENA_CLASS.value)])
            fixed_arena_specs = dm.query(filters=[('build_type', '=', BuildConstants.BuildType.FIXED_ARENA.value)])

            # Render template
            return render_template('fixed_arena_home.html', auth_config=auth_config, fixed_arenas=fixed_arenas,
                                   workspaces=workspaces, class_spec_list=class_specs,
                                   fixed_arena_spec_list=fixed_arena_specs)
        return redirect('/login', 403)


@fixed_arena_app.route('/class/<build_id>', methods=['GET'])
def class_landing(build_id):
    if user_email := session.get('user_email', None):
        auth = ArenaAuthorizer()
        if user := auth.authorized(email=user_email, base=auth.UserGroups.INSTRUCTOR):
            auth_config = cloud_env.auth_config
            attack_specs = DataStoreManager(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC).query()
            fa_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value, key_id=build_id).get()
            if fa_class:
                workspaces = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                                             parent_id=fa_class.key.name)
                return render_template('fixed_arena_class.html', auth_config=auth_config, fixed_arena_class=fa_class,
                                       workspaces=workspaces, attack_spec=attack_specs, main_app_url=cloud_env.main_app_url)
            abort(404)
    return redirect('/login', 403)

