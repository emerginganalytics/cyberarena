"""
Medical themed variant to normal IoT workout
"""
import json
from flask import abort, Blueprint, render_template, request, jsonify, make_response, url_for, redirect, flash
from app_utilities.gcp.cloud_env import CloudEnv
from google.api_core.exceptions import NotFound
from app_utilities.gcp.iot_manager import IotManager
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, Commands

iot_nsa_bp = Blueprint(
    'iot_nsa_bp', __name__,
    url_prefix='/healthcare',
    template_folder='templates',
    static_folder='static'
)

env = CloudEnv()
physician = 'BMTeNtG4FEZMhVA5MyDljul4LhcY4297'
nurse = 'jZnTtcKM4JL07Sq5PjGMM9eCsAnUUC6E'
guest = '3tR2aJ8BQgf99TRkE7xxHMQ4Q2lW5qFX'


@iot_nsa_bp.route('/', methods=['GET', 'POST'])
def setup():
    page_template = './nsa_iot_setup.jinja'
    if request.method == 'POST':
        resp = json.loads(request.data)
        device_id = resp['device_id']
        check_device = IotManager(device_id=device_id).check_device()
        if check_device:
            print(f'Received object {resp}')
            print(str(url_for('iot_nsa_bp.index', device_id=device_id)))
            resp = make_response(jsonify({'url': url_for('iot_nsa_bp.index', device_id=device_id)}))
            resp.set_cookie('uid', '2')
            return resp
        message = jsonify({'error_msg': f'Unrecognized device with ID: {device_id}'})
        return make_response(message, 400)
    return render_template(page_template)


@iot_nsa_bp.route('/faq', methods=['GET'])
def nsa_faq():
    page_template = './nsa_faq.jinja'
    return render_template(page_template, project=env.project)


@iot_nsa_bp.route('/iot/<device_id>', methods=['GET'])
def index(device_id):
    page_template = './index.jinja'

    # Used to get current registered device data
    auth = request.cookies.get('auth', guest)
    uid = request.args.get('uid', 2)
    if uid == 1 and auth in [physician, nurse]:
        valid_commands = Commands.healthcare(1)
    elif uid == 0 and auth == physician:
        valid_commands = Commands.healthcare(uid)
    else:
        valid_commands = Commands.healthcare(uid)
    iot_data = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=str(device_id)).get()
    if iot_data is not None:
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

    if request.method == 'GET':
        iot_data = IotManager(device_id=device_id).get()
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
    if request.method == 'POST':
        iot_mgr = IotManager(device_id)
        resp = json.loads(request.data)
        if command := resp.get('command'):
            if not (token := resp.get('token', None)) or token != physician:
                flash(f'403: Missing or invalid authentication token! You do not have permissions to run: {command}',
                      'alert-warning')
                return jsonify({'resp': 403})
            success, data = iot_mgr.msg(command, device_type=555555)
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


@iot_nsa_bp.route('/token/', methods=['GET'])
def get_token():
    if args := request.args.get('auth', None):
        auth = args.get('auth', 'guest')
        if auth == 'physician':
            level = 0
            token = physician
        elif auth == 'nurse':
            level = 1
            token = nurse
        else:
            level = 2
            token = guest
        resp = make_response(jsonify({'token': token}))
        resp.set_cookie('uid', str(level))
        return resp
    return jsonify({'resp': 400})


def _validate(cmd, token):
    cmd = Commands.validate(cmd, token)
    if token:
        return cmd
    return False
