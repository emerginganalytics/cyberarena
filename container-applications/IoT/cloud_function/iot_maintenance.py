import base64
import logging
import json
import pytz
from datetime import datetime, timedelta

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.iot_manager import IotManager
from cloud_fn_utilities.globals import DatastoreKeyTypes


class IotCloudMaintenance:
    def __init__(self, attributes=None, dataflow=None, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if not env_dict else env_dict
        self.env_dict = self.env.get_env()
        self.attributes = attributes
        self.dataflow = self._decode(dataflow) if dataflow else None
        self.data = None
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE)
        self.device_num_id = None
        self.device_id = None
        self.expire_hours = 3
        self.now = self._get_local_time()
        if 0 <= self.now.minute <= 16:
            self.hourly = True
        else:
            self.hourly = False

    def msg(self):
        # First make any updates to Iot device records
        self.device_id = self.attributes.get('deviceId', None)
        self.device_num_id = self.attributes.get('deviceNumId', None)
        if self.device_id and self.device_num_id:
            self._update()

    def maintenance(self):
        if self.hourly:
            # self._reset_records()
            print('I am not cleaning anything ([==]o[==])')

    def _update(self):
        device = self.ds.get(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=str(self.device_id))
        if not device:
            logging.info('Device not found; Adding device to datastore')
            print('Device not found; Adding device to datastore')
            return self._create()
        else:
            logging.info(f'Updating device : {self.device_num_id}')
            if system_data := self.dataflow.get('system', None):
                device['memory'] = system_data.get('memory', None)
                device['ip'] = system_data.get('ip', None)
                device['storage'] = system_data.get('storage', None)
            if sensor_data := self.dataflow.get('sensor_data', None):
                if car := sensor_data.get('car', None):
                    if car != device['car']:
                        device['car'] = car
                if patients := sensor_data.get('patients', None):
                    if patients != device['patients']:
                        device['patients'] = patients
                if color := sensor_data.get('color', None):
                    if color != device['sensor_data'].get('color', None):
                        device['sensor_data']['color'] = color
                if flag := sensor_data.get('flag', None):
                    if flag != device.get('flag', None):
                        device['flag'] = flag
            # Finally Update Timestamp
            device['ts'] = self.now.timestamp()
            self.ds.put(device, key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=str(self.device_id))

    def _reset_records(self):
        if devices := self.ds.query():
            expire_time = (self.now - timedelta(hours=self.expire_hours)).timestamp()
            update = []
            for device in devices:
                if last_seen := device.get('ts', False):
                    if last_seen < expire_time:
                        update.append(self.ds.entity(self._clean(device)))
                    else:
                        continue
            if len(update) > 0:
                self.ds.put_multi(devices)
                logging.info(f'Records reset')
            else:
                logging.info(f'No updates required; Quitting ...')
        else:
            logging.info('No device records found! Quitting ...')

    def _create(self):
        device_id = self.attributes.get('deviceId', None)
        device_num_id = self.attributes.get('deviceNumId', None)
        if not device_id:
            logging.error('Missing deviceId or deviceNumId found for iot device')
            raise ValueError
        # Split the sensor data from the remainder of the object
        split_data = self._split_sensor_data(self.dataflow['sensor_data'])
        device = {
            'id': device_id,
            'num_id': device_num_id,
            'ts': self.now.timestamp(),
            'ip': self.dataflow['system'].get('ip', None),
            'memory': self.dataflow['system'].get('memory', None),
            'storage': self.dataflow['system'].get('storage', None),
            'misc': []
        }
        device.update(split_data)
        # for key, val in enumerate(split_data):
        #    device[key] = val

        # Create and return object
        self.ds.put(device, key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=str(device_id))
        logging.info(f'Added {device_id} to Datastore ...')
        return device

    def _get_local_time(self):
        now = datetime.now()
        timezone = pytz.timezone(self.env.timezone)
        return timezone.localize(now)

    @staticmethod
    def _decode(base64Str):
        try:
            data = base64.b64decode(base64Str).decode('UTF-8')
            if type(data) == str:
                print(data)
                return json.loads(data)
        except Exception:
            logging.error('Method failed to process data str; Object is not base64 decodable!')

    @staticmethod
    def _clean(device):
        for key, value in enumerate(device):
            if key in ['patients', 'car']:
                value = {}
            elif key == 'flag':
                value = ''
        return device

    @staticmethod
    def _split_sensor_data(sensor_data):
        return {
            'flag': sensor_data.get('flag', ''),
            'car': sensor_data.get('car', {}),
            'patients': sensor_data.get('patients', {}),
            'sensor_data': {
                'heart': sensor_data['heart'],
                'humidity': sensor_data['humidity'],
                'pressure': sensor_data['pressure'],
                'temp': sensor_data['temp'],
                'orientation': {
                    'z': sensor_data['z'],
                    'x': sensor_data['x'],
                    'y': sensor_data['y'],
                },
                'color': sensor_data['color']
            }
        }
