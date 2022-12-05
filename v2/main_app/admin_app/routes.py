import json
import logging as logger
from flask import abort, Blueprint, render_template, redirect, request
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.compute_manager import ComputeManager

admin_app = Blueprint('admin', __name__, url_prefix="/admin",
                      static_folder="./static", template_folder="./email_templates")
# TODO: Move each API call to its respective API file:
#           admin_app.register_blueprint(admin_api)


@admin_app.route('/home', methods=['GET', 'POST'])
def admin_page():
    admin_info = ArenaAuthorizer().admin_info
    comment_query = DataStoreManager(key_id='cybergym-comments').query()
    comment_query.order = ['date']
    comment_list = comment_query.fetch()
    comments = []
    active_workouts = []
    for comment in comment_list:
        comments.append(comment)
    instance_list = ComputeManager().get_instances()

    if request.method == "POST":
        response = {
            'action_completed': 'false'
        }
        data = request.get_json(force=True)
        if data['action'] == 'approve_user':
            if data['user_email'] in admin_info['pending']:
                admin_info['authorized_users'].append(data['user_email'])
                admin_info['pending'].remove(data['user_email'])
                response['action_completed'] = 'true'
                message = "User {} approved for general access".format(data['user_email'])
                logger.info(msg=message)
        elif data['action'] == 'deny_user':
            if data['user_email'] in admin_info['pending']:
                admin_info['pending'].remove(data['user_email'])
                response['action_completed'] = 'true'
                message = "User {} denied general access".format(data['user_email'])
                logger.info(msg=message)
        elif data['action'] == 'promote_user':
            if data['user_email'] in admin_info['authorized_users']:
                admin_info['admins'].append(data['user_email'])
                response['action_completed'] = 'true'
                message = "User {} granted administrator privileges".format(data['user_email'])
                logger.info(msg=message)
        elif data['action'] == 'remove_user':
            if data['user_email'] in admin_info['authorized_users']:
                admin_info['authorized_users'].remove(data['user_email'])
                response['action_completed'] = 'true'
                message = "User {} removed".format(data['user_email'])
                logger.info(msg=message)
        elif data['action'] == 'revoke_access':
            if data['user_email'] in admin_info['admins']:
                admin_info['admins'].remove(data['user_email'])
                response['action_completed'] = 'true'
                message = "User {} is no longer an administrator".format(data['user_email'])
                logger.info(msg=message)
        DataStoreManager().put(obj=admin_info)
        return json.dumps(response)
    # admin_actions = {key: value for key, value in AdminActions.__dict__.items() if not (key.startswith('__') and key.endswith('__'))}
    admin_actions = {}
    return render_template('admin_page.html', auth_config=CloudEnv().auth_config, admin_info=admin_info,
                           admin_actions=admin_actions, active_workouts=active_workouts,
                           comments=comments, instance_list=json.dumps(instance_list))


@admin_app.route('/<workout_id>', methods=['GET', 'POST'])
def admin_workout(workout_id):
    workout = DataStoreManager(DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=workout_id)
    if workout:
        workout_server_query = DataStoreManager(key_id=workout_id).get_servers()
        server_list = []
        for server in workout_server_query:
            server_list.append(server)
        return render_template('admin_workout.html', workout=workout, servers=server_list)
    else:
        abort(404)


@admin_app.route('/iot_device/<device_id>', methods=['GET'])
def iot_device(device_id):
    device = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=device_id)
    if device:
        return render_template('iot_device.html', device=device)
    else:
        abort(404)


'''
@admin_app.route('/update_base', methods=['POST'])
def update_base():
    """
    def store_background_color(color_code):
        css_string = ':root{--main_color: %s}' % (color_code)
        temp_css = open('temp.css', 'w')
        temp_css.write(css_string)
        temp_css.close()

        bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
        new_blob = bucket.blob('color/{}-base.css'.format(project))

        # Prevent GCP from serving a cached version of this file
        new_blob.cache_control = 'private'
        new_blob.upload_from_string(css_string, content_type='text/css')

        remove('temp.css')
    """
    if request.method == "POST":
        if 'custom_color' in request.form:
            store_background_color(request.form['custom_color'])
            message = "Updated background color to {}".format(request.form['custom_color'])
            logger.info(msg=message)
    return redirect('/admin/home')
'''

