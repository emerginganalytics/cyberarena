import json
from flask import abort, Blueprint, jsonify, render_template, redirect, request, session
from utilities.datastore_functions import *
from utilities.globals import AdminActions, auth_config, compute, dns_suffix, ds_client, log_client, logger, LOG_LEVELS, \
    workout_token, post_endpoint, main_app_url, project, region, zone
from utilities.iot_manager import IotManager
from utilities.pubsub_functions import *
from utilities.workout_validator import WorkoutValidator
from utilities.iot_manager import IotManager
from admin_app.admin_api import admin_api

admin_app = Blueprint('admin', __name__, url_prefix="/admin",
                      static_folder="./static", template_folder="./templates")
admin_app.register_blueprint(admin_api)


@admin_app.route('/home', methods=['GET', 'POST'])
def admin_page():
    admin_info = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
    comment_query = ds_client.query(kind='cybergym-comments')
    comment_query.order = ['date']
    comment_list = comment_query.fetch()
    comments = []
    active_workouts = []
    for comment in comment_list:
        comments.append(comment)
        
    instance_list = []
    machine_instances = compute.instances().list(project=project, zone=zone, filter=("name:cybergym-*")).execute()
    if 'items' in machine_instances:
        for instance in machine_instances['items']:
            if 'name' in instance:
                instance_list.append(str(instance['name']))

    if request.method == "POST":
        response = {
            'action_completed': 'false'
        }
        data = request.get_json(force=True)
        if data['action'] == 'approve_user':
            if data['user_email'] in admin_info['pending']:
                admin_info['authorized_users'].append(data['user_email'])
                admin_info['pending'].remove(data['user_email'])
                ds_client.put(admin_info)
                response['action_completed'] = 'true'
                g_logger = log_client.logger('admin-app')
                g_logger.log_struct(
                    {
                        "message": "User {} approved for general access".format(data['user_email'])
                    }, severity=LOG_LEVELS.INFO
                )
        elif data['action'] == 'deny_user':
            if data['user_email'] in admin_info['pending']:
                admin_info['pending'].remove(data['user_email'])
                ds_client.put(admin_info)
                response['action_completed'] = 'true'
                g_logger = log_client.logger('admin-app')
                g_logger.log_struct(
                    {
                        "message": "User {} denied general access".format(data['user_email'])
                    }, severity=LOG_LEVELS.INFO
                )
        elif data['action'] == 'promote_user':
            if data['user_email'] in admin_info['authorized_users']:
                admin_info['admins'].append(data['user_email'])
                ds_client.put(admin_info)
                response['action_completed'] = 'true'
                g_logger = log_client.logger('admin-app')
                g_logger.log_struct(
                    {
                        "message": "User {} granted administrator privileges".format(data['user_email'])
                    }, severity=LOG_LEVELS.INFO
                )
        elif data['action'] == 'remove_user':
            if data['user_email'] in admin_info['authorized_users']:
                admin_info['authorized_users'].remove(data['user_email'])
                ds_client.put(admin_info)
                response['action_completed'] = 'true'
                g_logger = log_client.logger('admin-app')
                g_logger.log_struct(
                    {
                        "message": "User {} removed".format(data['user_email'])
                    }, severity=LOG_LEVELS.INFO
                )
        elif data['action'] == 'revoke_access':
            if data['user_email'] in admin_info['admins']:
                admin_info['admins'].remove(data['user_email'])
                ds_client.put(admin_info)
                response['action_completed'] = 'true'
                g_logger = log_client.logger('admin-app')
                g_logger.log_struct(
                    {
                        "message": "User {} is no longer an administrator".format(data['user_email'])
                    }, severity=LOG_LEVELS.INFO
                )
        return json.dumps(response)
    admin_actions = {key: value for key, value in AdminActions.__dict__.items() if not (key.startswith('__') and key.endswith('__'))}
    # print(admin_actions)
    return render_template('admin_page.html', auth_config=auth_config, admin_info=admin_info,
                           admin_actions=admin_actions, active_workouts=active_workouts,
                           comments=comments, instance_list=json.dumps(instance_list))


@admin_app.route('/<workout_id>', methods=['GET', 'POST'])
def admin_workout(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    if workout:
        workout_server_query = ds_client.query(kind='cybergym-server')
        workout_server_query.add_filter('workout', '=', workout_id)
        server_list = []
        for server in list(workout_server_query.fetch()):
            server_list.append(server)
        return render_template('admin_workout.html', workout=workout, servers=server_list)
    else:
        abort(404)


@admin_app.route('/iot_device/<device_id>', methods=['GET'])
def iot_device(device_id):
    device = ds_client.get(ds_client.key(IotManager().kind, device_id))
    if device:
        return render_template('iot_device.html', device=device)
    else:
        abort(404)


@admin_app.route('/update_base', methods=['POST'])
def update_base():
    if request.method == "POST":
        if 'custom_color' in request.form:
            store_background_color(request.form['custom_color'])
            g_logger = log_client.logger('admin-app')
            g_logger.log_struct(
                {
                    "message": "Updated background color to {}".format(request.form['custom_color'])
                }, severity=LOG_LEVELS.INFO
            )
    return redirect('/admin/home')


@admin_app.errorhandler(500)
def handle_500(e):
    g_logger = log_client.logger('cybergym-app-errors')
    g_logger.log_struct(
        {
            "error_type": 500,
            "details": str(e),
            "request": str(request)
        }
    )
    return render_template("errors/500.html", error=e), 500


@admin_app.errorhandler(404)
def handle_404(e):
    g_logger = log_client.logger('cybergym-app-errors')
    g_logger.log_struct(
        {
            "error_type": 404,
            "details": str(e),
            "request": str(request)
        }
    )
    return render_template("errors/404.html")