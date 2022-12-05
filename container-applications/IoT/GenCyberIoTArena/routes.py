from flask import Blueprint, render_template, request, jsonify, make_response, url_for, redirect, flash
from globals import project
from google.cloud import iot_v1
import json

# Blueprint configuration
iot_arena_bp = Blueprint(
    'iot_arena_bp', __name__, 
    url_prefix='/iot_arena',
    template_folder='email_templates',
    static_folder='static'
)


@iot_arena_bp.route('/', methods=['GET', 'POST'])
def setup():
    page_template = './iot_arena_setup.jinja'
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'

    # Initiate IoT client and get list of all registered IoT devices in project
    iot_client = iot_v1.DeviceManagerClient()
    devices_gen = iot_client.list_devices(parent=f'projects/{project}/locations/{cloud_region}/registries/{registry_id}')
    device_list = [i.id for i in devices_gen]

    if request.method == 'POST':
        print(request.data)
        resp = json.loads(request.data)
        device_id = resp['device_id']
        check_device = True if device_id in device_list else False
        if check_device:
            print(f'Recieved object {resp}')
            print(str(url_for('iot_arena_bp.index', device_id=device_id)))
            return jsonify({'url': url_for('iot_arena_bp.index', device_id=device_id)})
        message = jsonify({'error_msg': f'Unrecognized device with ID: {device_id}'})
        return make_response(message, 400)
    return render_template(page_template)


@iot_arena_bp.route('/arena_commands/<device_id>', methods=['GET', 'POST'])
def index(device_id):
    return render_template('./iot_arena.jinja', device_id=device_id)


@iot_arena_bp.route('/arena_commands/<device_id>/submit', methods=['POST'])
def submit(device_id):
    user_input = request.get_json(force=True)
    print(user_input)
    if(user_input == '5720'):
        return redirect(url_for('iot_arena_bp.flag', device_id=device_id))

    return jsonify(user_input)


@iot_arena_bp.route('/unlock/<device_id>', methods=['GET'])
def unlock(device_id):
    if request.method == 'GET':
        user_input = request.args['secret_code']
        print(user_input)
        if user_input == '5720':
            return redirect(url_for('iot_arena_bp.flag', device_id=device_id))
        else:
            flash("Incorrect code. Please try again")
            return redirect(url_for('iot_arena_bp.index', device_id=device_id))
        

@iot_arena_bp.route('/arena/<device_id>/flag', methods=['GET'])
def flag(device_id):
    return render_template('./iot_flag.jinja', device_id=device_id)
