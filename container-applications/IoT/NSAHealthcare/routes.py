"""
Medical themed variant to normal IoT workout
"""
import json
from flask import abort, Blueprint, render_template, request, jsonify, make_response, url_for, redirect, flash
from globals import project
from google.api_core.exceptions import NotFound
from google.cloud import iot_v1
from iot_database import IOTDatabase

iot_nsa_bp = Blueprint(
    'iot_nsa_bp', __name__,
    url_prefix='/healthcare',
    template_folder='templates',
    static_folder='static'
)


@iot_nsa_bp.route('/', methods=['GET', 'POST'])
def setup():
    page_template = './nsa_iot_setup.jinja'
    iot_client = iot_v1.DeviceManagerClient()
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'
    devices_gen = iot_client.list_devices(
        parent=f'projects/{project}/locations/{cloud_region}/registries/{registry_id}')
    device_list = [i.id for i in devices_gen]

    if request.method == 'POST':
        print(request.data)
        resp = json.loads(request.data)
        device_id = resp['device_id']
        check_device = True if device_id in device_list else False
        if check_device:
            print(f'Recieved object {resp}')
            print(str(url_for('iot_nsa_bp.index', device_id=device_id)))
            return jsonify({'url': url_for('iot_nsa_bp.index', device_id=device_id)})
        message = jsonify({'error_msg': f'Unrecognized device with ID: {device_id}'})
        return make_response(message, 400)
    return render_template(page_template)


@iot_nsa_bp.route('/faq', methods=['GET'])
def nsa_faq():
    page_template = './nsa_faq.jinja'
    return render_template(page_template, project=project)


@iot_nsa_bp.route('/iot/<device_id>', methods=['GET'])
def index(device_id):
    page_template = './index.jinja'

    # Used to get current registered device data
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'
    client = iot_v1.DeviceManagerClient()  # publishes to device
    iotdb = IOTDatabase()
    device_path = client.device_path(project, cloud_region, registry_id, device_id)
    device_num_id = str(client.get_device(request={"name": device_path}).num_id)
    valid_commands = ['HEART', 'PRESSURE', 'HUMIDITY', 'TEMP',]

    iot_data = None
    if device_num_id:
        iot_data = iotdb.get_rpi_sense_hat_data(device_num_id=device_num_id)
    if iot_data is not None:
        iot_data['sensor_data'] = json.loads(iot_data['sensor_data'])
        iot_data['sensor_data']['heart'] = iot_data['sensor_data']['heart'].split(" ")[0]
        iot_temp = int(float(iot_data['sensor_data']['temp'].split('f')[0]))
        iot_hum = int(float(iot_data['sensor_data']['humidity'].split('%')[0]))
        iot_pres = int(float(iot_data['sensor_data']['pressure'].split(' ')[0]))
        print(f'database query returned: {iot_data}')
        return render_template(
            page_template,
            commands=valid_commands,
            device_id=device_id,
            iot_data=iot_data,
            iot_temp=iot_temp,
            iot_hum=iot_hum,
            iot_pres=iot_pres,
        )
    flash("Couldn\'t connect to device. Is it online?")
    return redirect(url_for('iot_nsa_bp.setup'))


@iot_nsa_bp.route('/iot/patients/<device_id>', methods=['GET', 'POST'])
def patients(device_id):
    # TODO: WIP; Tie in to bp.index page to allow students to 'leak' critical web information
    #       based on either: command sent to pi or by utilizing data already received from
    #       pi on previously revealed flags
    page_template = './classified.jinja'

    # Used to get current registered device data
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'
    iotdb = IOTDatabase()
    client = iot_v1.DeviceManagerClient()
    device_path = client.device_path(project, cloud_region, registry_id, device_id)
    device_num_id = str(client.get_device(request={"name": device_path}).num_id)

    # page data
    auth_cookie = request.cookies.get('authed')
    medical_data = [
        {'id': 1, 'name': 'Gabriel Tawfeek', 'age': 26, 'ssn': '897-822-104', 'blood_type': 'AB-'},
        {'id': 2, 'name': 'Ásta Božić', 'age': 33, 'ssn': '548-562-085', 'blood_type': 'A+'},
        {'id': 3, 'name': 'Hanife Mulloy', 'age': 64, 'ssn': '633-316-962', 'blood_type': 'O+'},
        {'id': 4, 'name': 'Alex Stenberg', 'age': 40, 'ssn': '134-316-696', 'blood_type': 'A+'},
        {'id': 5, 'name': 'Zoë Fields', 'age': 19, 'ssn': '602-337-539', 'blood_type': 'B+'},
    ]
    classified_flag = "CyberArena{Yg9ttKzAA9}"

    iot_data = None
    if request.method == 'GET':
        if device_num_id:
            iot_data = iotdb.get_rpi_sense_hat_data(device_num_id=device_num_id)
        if iot_data is not None:
            return render_template(
                page_template,
                device_id=device_id,
                medical_data=medical_data,
                classified_flag=classified_flag,
            )
        flash("Couldn\'t connect to device. Is it online?")
        return redirect(url_for('iot_nsa_bp.setup'))
    elif request.method == 'POST':
        resp = json.loads(request.data)
        command = resp['command']
        data = command.encode("utf-8")
        print("[+] Publishing to device topic")
    else:
        return abort(404)


@iot_nsa_bp.route('/iot/<device_id>/submit', methods=['POST'])
def submit(device_id):
    cloud_region = 'us-central1'
    registry_id = 'cybergym-registry'

    # Init Publisher client for server
    client = iot_v1.DeviceManagerClient()
    device_path = client.device_path(project, cloud_region, registry_id, device_id)
    if request.method == 'POST':
        resp = json.loads(request.data)
        command = resp['command']
        data = command.encode("utf-8")
        # Try publishing to device topic
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
