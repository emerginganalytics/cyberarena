from google.cloud import iot_v1
from flask import Blueprint, request, redirect
from utilities.pubsub_functions import pub_admin_scripts, pub_manage_server
from utilities.globals import ds_client, project, log_client, compute, zone, LOG_LEVELS, AdminActions, workout_globals
from utilities.yaml_functions import generate_yaml_content, parse_workout_yaml, save_yaml_file
from utilities.datastore_functions import store_custom_logo, store_background_color, upload_instruction_file
import json

admin_api = Blueprint('admin_api', __name__, url_prefix='/api')


@admin_api.route('/active_workouts', methods=['GET'])
def get_active_workouts():
    active_workout_query = ds_client.query(kind='cybergym-workout')
    
    workout_list = active_workout_query.fetch()
    active_workouts = []

    for workout in workout_list:
        if 'state' in workout:
            if workout['state'] != "DELETED" and workout['state'] != "COMPLETED_DELETING_SERVERS":
                if 'hourly_cost' in workout and 'runtime_counter' in workout:
                    if workout['hourly_cost'] and workout['runtime_counter']:
                        estimated_cost = (float(workout['hourly_cost']) / 3600) * float(workout['runtime_counter'])
                        workout['estimated_cost'] = format(estimated_cost, '.2f')
                workout['id'] = workout.key.name
                active_workouts.append(workout)
    return json.dumps(active_workouts)


@admin_api.route('/registered_iot_devices', methods=['GET'])
def get_iot_devices():
    iot_client = iot_v1.DeviceManagerClient()
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'
    devices_gen = iot_client.list_devices(
        parent=f'projects/{project}/locations/{cloud_region}/registries/{registry_id}')
    iot_device_list = [i.id for i in devices_gen]


@admin_api.route("/admin_scripts", methods=['POST'])
def admin_scripts():
    if request.method == 'POST':
        request_data = request.form.to_dict()
        command_dict = {}
        command_dict["params"] = {}
        for key, value in request_data.items():
            if key == 'function_name':
                command_dict["function_name"] = value.lower()
            else:
                command_dict["params"].update({key: value})

        pub_admin_scripts(json.dumps(command_dict))
        return json.dumps({str(command_dict['function_name']): 'Command Sent'})


@admin_api.route('/update_logo', methods=['POST'])
def update_logo():
    if request.method == "POST":
        data = request.files['custom_logo']
        store_custom_logo(data)
        g_logger = log_client.logger('admin-app')
        g_logger.log_struct(
            {
                "message": "Updating logo image"
            }, severity=LOG_LEVELS.INFO
        )
    return redirect('/admin/home')


@admin_api.route('/update_workout_list', methods=["POST"])
def update_workout_list():
    if request.method == 'POST':
        if 'new_workout_name' and 'new_workout_display' in request.form:
            admin_info = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
            workout_list = admin_info['workout_list']
            if not any(workout['workout_name'] == request.form['new_workout_name'] for workout in workout_list):
                new_workout_info = {
                    'workout_name': request.form['new_workout_name'],
                    'workout_display_name': request.form['new_workout_display']
                }
                workout_list.append(new_workout_info)
                ds_client.put(admin_info)
                return 'Complete'
            else:
                return 'Failed'
        else:
            return 'Failed'


@admin_api.route('/server_management/<workout_id>', methods=['POST'])
def admin_server_management(workout_id):
    if request.method == 'POST':
        data = request.json
        if 'action' in data:
            g_logger = log_client.logger('admin-app')
            g_logger.log_struct(
                {
                    "message": "{} action called for server {}".format(data['action'], data['server_name'])
                }, severity=LOG_LEVELS.INFO
            )
            pub_manage_server(data['server_name'], data['action'])
    return 'True'


@admin_api.route('/change_workout_state', methods=['POST'])
def change_workout_state():
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        response = {}
        response['workout_id'] = request_data['workout_id']
        response['new_state'] = request_data['new_state']

        workout = ds_client.get(ds_client.key('cybergym-workout', request_data['workout_id']))
        if 'state' in workout:
            previous_state = workout['state']
        workout['state'] = request_data['new_state']
        g_logger = log_client.logger('admin-app')
        g_logger.log_struct(
            {
                "message": "Workout {} state override: {} to {}".format(request_data['workout_id'], previous_state, request_data['new_state']),
                "previous_state": str(previous_state),
                "new_state": str(request_data['new_state']),
                "workout": str(request_data['workout_id'])
            }, severity=LOG_LEVELS.INFO
        )
        ds_client.put(workout)
        return json.dumps(response)


@admin_api.route('/change_workout_expiration', methods=['POST'])
def change_workout_expiration():
    if request.method == "POST":
        request_data = request.get_json(force=True)
        if 'workout_id' in request_data:
            workout = ds_client.get(ds_client.key('cybergym-workout', request_data['workout_id']))
            workout['expiration'] = request_data['new_expiration']
            ds_client.put(workout)
        return json.dumps(str("Test"))


@admin_api.route('/create_workout_spec', methods=['POST'])
def create_workout_spec():
    if request.method == 'POST':
        request_data = request.get_json(force=True)

        yaml_string = generate_yaml_content(request_data)
        return json.dumps(yaml_string)


@admin_api.route('/save_workout_spec', methods=['POST'])
def save_workout_spec():
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        save_yaml_file(request_data)
        response = {}
        response['completed'] = True
        admin_info = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
        workout_entry = str(request_data['workout']['name'])
        if 'workout_list' not in admin_info:
            admin_info['workout_list'] = []
        g_logger = log_client.logger('admin-app')
        g_logger.log_struct(
            {
                "message": "Created new workout specification",
                "new_workout_type": workout_entry
            }, severity=LOG_LEVELS.INFO
        )
        admin_info['workout_list'].append(workout_entry.replace(" ", "").lower())
        ds_client.put(admin_info)

        return json.dumps(response)


@admin_api.route('/instance_info', methods=["POST"])
def instance_info():
    if request.method == "POST":
        data = request.get_json()
        if 'instance' in data:
            instance_query = compute.instances().list(project=project, zone=zone, filter=("name:"+data['instance'])).execute()
            instance_info = {}
            instance_details = instance_query['items'][0]
            nics = []
            if 'networkInterfaces' in instance_details:
                for nic in instance_details['networkInterfaces']:
                    nic_info = {}
                    if 'networkIP' in nic:
                        nic_info['ip'] = nic['networkIP']
                    nics.append(nic_info)
            instance_info['nics'] = nics

        return json.dumps(instance_info)


@admin_api.route('/upload_instructions', methods=['POST'])
def upload_instructions():
    if request.method == 'POST':
        if 'teacher_instruction_file' in request.files:
            teacher_instruction_file = request.files['teacher_instruction_file']
            upload_instruction_file(teacher_instruction_file, workout_globals.teacher_instruction_folder, teacher_instruction_file.filename)
        if 'student_instruction_file' in request.files:
            student_instruction_file = request.files['student_instruction_file']
            upload_instruction_file(student_instruction_file, workout_globals.student_instruction_folder, student_instruction_file.filename)
        return json.dumps({"Upload":True})
