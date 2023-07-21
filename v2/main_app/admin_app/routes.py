import json
import logging as logger
from flask import abort, Blueprint, render_template, redirect, request, session, url_for
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, get_current_timestamp_utc, BuildConstants
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer

admin_app = Blueprint('admin', __name__, url_prefix="/admin",
                      static_folder="./static", template_folder="./templates")
cloud_env = CloudEnv()


@admin_app.route('/dashboard', methods=['GET'])
def home():
    workout_list = []
    if user_email := session.get('user_email', None):
        auth = ArenaAuthorizer()
        if user := auth.authorized(user_email, base=auth.UserGroups.ADMIN):
            admin_info = auth.get_all_users()
            active_filter = [('workspace_settings.expires', '>', get_current_timestamp_utc())]
            active_units = DataStoreManager(key_type=DatastoreKeyTypes.UNIT).query(filters=active_filter)
            return render_template('v2-admin-home.html', auth_config=cloud_env.auth_config, workout_list=workout_list,
                                   admin_info=admin_info, auth_list=user['permissions'], active_units=active_units)
    return redirect('/login')


@admin_app.route('/dashboard/manage/workout/<build_id>', methods=['GET'])
def manage(build_id):
    workout_list = []
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id).get()
    unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=workout['parent_id']).get()
    servers = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.SERVER, parent_id=workout['id'])

    return render_template('manage-workout.html', workout=workout, unit=unit, servers=servers)


@admin_app.route('/iot_device/<device_id>', methods=['GET'])
def iot_device(device_id):
    device = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=device_id)
    if device:
        return render_template('iot_device.html', device=device)
    else:
        abort(404)


def _generate_urls():
    urls = {
        'unit': url_for('unit'),
        'escape_room': url_for('escape-room'),
        'fixed_arena': url_for('fixed-arena'),
        'fixed_arena_class': url_for('class'),
    }