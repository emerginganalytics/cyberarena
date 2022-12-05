import json
from flask import Blueprint, flash, jsonify, redirect, render_template, request, make_response, url_for
from globals import project
from google.api_core.exceptions import NotFound
from google.cloud import iot_v1
from iot_database import IOTDatabase

# Blueprint Configuration
iot_bp = Blueprint(
    'iot_bp', __name__,
    url_prefix='/iot',
    template_folder='email_templates',
    static_folder='static'
)


@iot_bp.route('/', methods=['GET', 'POST'])
def setup():
    page_template = './iot_setup.jinja'
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
            return jsonify({'url': url_for('iot_bp.index', device_id=device_id)})
        message = jsonify({'error_msg': f'Unrecognized device with ID: {device_id}'})
        return make_response(message, 400)
    return render_template(page_template)


@iot_bp.route('/faq', methods=['GET'])
def faq():
    page_template = './faq.jinja'
    return render_template(page_template, project=project)


@iot_bp.route('/commands/<device_id>', methods=['GET'])
def index(device_id):
    page_template = './iot.jinja'

    # Used to get current registered device data
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'
    client = iot_v1.DeviceManagerClient()  # publishes to device
    iotdb = IOTDatabase()
    device_path = client.device_path(project, cloud_region, registry_id, device_id)
    device_num_id = str(client.get_device(request={"name": device_path}).num_id)
    print(device_num_id)

    # Pass level_1 flag back in override var to unlock level_2 of the challenge
    override = None
    # Supported Commands; Passed through template to generate buttons
    commands = {
        # banned_commands = ['green']
        'functions': ['humidity', 'heart', 'pressure', 'temp'],
        'colors': ['red', 'orange', 'yellow', 'purple', 'blue', 'teal']
    }

    iot_data = None
    if device_num_id:
        iot_data = iotdb.get_rpi_sense_hat_data(device_num_id=device_num_id)
    if iot_data is not None:
        iot_data['sensor_data'] = json.loads(iot_data['sensor_data'])
        print(f'database query returned: {iot_data}')
        return render_template(
            page_template,
            device_id=device_id,
            commands=commands,
            override=override,
            iot_data=iot_data
        )
    flash("Couldn\'t connect to device. Is it online?")
    return redirect(url_for('iot_bp.setup'))


@iot_bp.route('/commands/<device_id>/submit', methods=['POST'])
def submit(device_id):
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'

    # Init Publisher client for server
    client = iot_v1.DeviceManagerClient()  # publishes to device
    device_path = client.device_path(project, cloud_region, registry_id, device_id)
    if request.method == 'POST':
        resp = json.loads(request.data)
        command = resp['command']
        data = command.encode("utf-8")
        print("[+] Publishing to device topic")
        try:
            client.send_command_to_device(
                request={"name": device_path, "binary_data": data}
            )
        except NotFound as e:
            print(e)
            flash(f'Device {device_id} responded with 404. Ensure the device is properly connected.', 'alert-warning')
            return jsonify(error=e)
        except Exception as e:
            return jsonify(error=e)
        finally:
            return jsonify(success=True)
    else:
        return jsonify({'resp': 404})
