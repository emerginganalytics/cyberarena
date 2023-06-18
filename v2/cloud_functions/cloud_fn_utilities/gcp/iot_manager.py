import pytz
from datetime import datetime, timedelta

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes


class IotManager:
    def __init__(self, device_id=None, dataflow=None, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if not env_dict else env_dict
        self.env_dict = self.env.get_env()
        self.device_id = device_id
        self.dataflow = dataflow
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=self.device_id)
        self.now = self._get_local_time()

    def update(self):
        device = self.ds.get()
        if not device:
            return self._create()
        else:
            if system_data := self.dataflow.get('system', None):
                device['memory'] = system_data.get('memory', None)
                device['ip'] = system_data.get('ip', None)
                device['storage'] = system_data.get('storage', None)
            if car := self.dataflow.get('car', None):
                device['car'] = car
            if patients := self.dataflow.get('patients', None):
                device['patients'] = patients
            self.ds.put(device)

    def reset_records(self):
        devices = self.ds.query()
        expire_time = (self.now - timedelta(hours=1)).timestamp()
        for device in devices:
            if last_seen := device.get('ts', False):
                if last_seen < expire_time:
                    device = self._clean(device)
                else:
                    continue
        DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE).put_multi(devices)

    def _get_local_time(self):
        now = datetime.now()
        timezone = pytz.timezone(self.env.timezone)
        return timezone.localize(now)

    def _create(self):
        # First we need to remove extra data points from the dict
        system = self.dataflow.pop('system', {})
        car = self.dataflow.pop('car', {})
        flag = self.dataflow.pop('flag', '')
        healthcare = self.dataflow.pop('patients', {})
        # Generate the ds object
        device = {
            'id': self.device_id,
            'ts': self.now.timestamp(),
            'sensor_data': self.dataflow.get('sensor_data', ''),
            'car': {},
            'patients': {},
            'ip': system.get('ip', ''),
            'memory': system.get('memory', ''),
            'storage': system.get('storage', ''),
            'flag': '',
        }
        # Create and return object
        self.ds.put(device, key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=self.device_id)
        return device

    @staticmethod
    def _clean(device):
        for key, value in enumerate(device):
            if key in ['patients', 'car']:
                value = {}
            elif key == 'flag':
                value = ''
        return device
