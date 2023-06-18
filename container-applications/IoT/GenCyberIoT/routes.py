import json
from flask import Blueprint, flash, jsonify, redirect, render_template, request, make_response, url_for
from google.api_core.exceptions import NotFound
from app_utilities.gcp.iot_manager import IotManager
from app_utilities.gcp.cloud_env import CloudEnv

# Blueprint Configuration
iot_bp = Blueprint(
    'iot_bp', __name__,
    url_prefix='/iot',
    template_folder='templates',
    static_folder='static'
)

env = CloudEnv()


@iot_bp.route('/', methods=['GET', 'POST'])
def setup():
    page_template = './iot_setup.jinja'
    if request.method == 'POST':
        print(request.data)
        resp = json.loads(request.data)
        device_id = resp['device_id']
        iot_manager = IotManager(device_id=device_id)
        if check_device := iot_manager.check_device():
            print(f'Received object {resp}')
            return jsonify({'url': url_for('iot_bp.index', device_id=device_id)})
        message = jsonify({'error_msg': f'Unrecognized device with ID: {device_id}'})
        return make_response(message, 400)
    return render_template(page_template)


@iot_bp.route('/faq', methods=['GET'])
def faq():
    page_template = './faq.jinja'
    return render_template(page_template, project=env.project)


@iot_bp.route('/commands/<device_id>', methods=['GET'])
def index(device_id):
    page_template = './iot.jinja'
    iot_mgr = IotManager(device_id=device_id)

    # Pass level_1 flag back in override var to unlock level_2 of the challenge
    override = None
    # Supported Commands; Passed through template to generate buttons
    commands = {
        # banned_commands = ['green']
        'functions': ['humidity', 'pressure', 'temp'],
        'colors': ['red', 'orange', 'yellow', 'purple', 'blue', 'teal']
    }

    iot_data = None
    if (iot_data := iot_mgr.get()) and iot_data is not None:
        print(f'database query returned: {iot_data}')
        json_data = json.dumps(iot_data['sensor_data'])
        return render_template(
            page_template,
            device_id=device_id,
            commands=commands,
            override=override,
            iot_data=iot_data,
            iot_json=json.dumps(iot_data['sensor_data'])
        )
    flash("Couldn\'t connect to device. Is it online?")
    return redirect(url_for('iot_bp.setup'))


@iot_bp.route('/commands/<device_id>/submit', methods=['POST'])
def submit(device_id):
    if request.method == 'POST':
        iot_mgr = IotManager(device_id)
        resp = json.loads(request.data)
        if command := resp.get('command'):
            success, data = iot_mgr.msg(command)
            if success:
                return jsonify(success=True)
            else:
                if data[1] == NotFound:
                    flash(f'Device {device_id} responded with 404. Ensure the device is properly connected.',
                          'alert-warning')
                return jsonify(error=data[1])
        return jsonify({'resp': 400})
    else:
        return jsonify({'resp': 404})
