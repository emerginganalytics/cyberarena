"""
Medical themed variant to normal IoT workout
"""
import json
from flask import abort, Blueprint, render_template, request, jsonify, make_response, url_for, redirect, flash, session
from app_utilities.gcp.cloud_env import CloudEnv
from google.api_core.exceptions import NotFound
from app_utilities.gcp.iot_manager import IotManager
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, Commands, Tokens

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
    uid = request.cookies.get('uid', 2)
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
            sensor_data=json.dumps(iot_data['sensor_data']),
            iot_temp=iot_temp,
            iot_hum=iot_hum,
            iot_pres=iot_pres,
        )
    flash("Couldn\'t connect to device. Is it online?")
    return redirect(url_for('iot_nsa_bp.setup'))


@iot_nsa_bp.route('/iot/<device_id>/submit', methods=['POST'])
def submit(device_id):
    if request.method == 'POST':
        if session.get('_flashes', None):
            session['_flashes'].clear()
        iot_mgr = IotManager(device_id)
        resp = json.loads(request.data)
        if command := resp.get('command'):
            if not (token := resp.get('token', None)):
                flash(f'403: Missing or invalid authentication token! You do not have permissions to run: {command}',
                      'alert-warning')
                return jsonify({'resp': 403})
            if not _validate(command, token):
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


@iot_nsa_bp.route('/iot/<device_id>/token', methods=['GET'])
def get_token(device_id):
    uid = request.args.get('uid', 2)
    token, level = Tokens.token_by_uid(uid)
    resp = make_response(jsonify({'token': token}))
    resp.set_cookie('uid', str(level))
    return resp


def _validate(cmd, token):
    cmd = Commands.validate(cmd, token)
    if cmd:
        return cmd
    return False
