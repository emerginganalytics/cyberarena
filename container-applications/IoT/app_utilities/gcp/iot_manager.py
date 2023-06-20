import json
from google.api_core.exceptions import NotFound
from google.cloud import iot_v1

from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes


class IotManager:
    class Commands:
        BASE = ['CLEAR', 'CONNECTED', 'HUMIDITY', 'PRESSURE', 'TEMP', 'SNAKE']
        HEALTHCARE = ['CRITICAL', 'HEART', 'PATIENT']
        CAR = ['BRAKE', 'GAS', "RADIO", "VEHICLE", 'PRODUCTS']

    """
    Managing class to handle Publish messages used by Cloud Run container
    """
    def __init__(self, device_id):
        self.device_id = device_id
        self.env = CloudEnv()
        self.project = self.env.project
        self.cloud_region = 'us-central1'
        self.registry_id = 'cybergym-registry'
        self.client = iot_v1.DeviceManagerClient()
        self.device_path = self._set_path()
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=device_id)

    def _set_path(self):
        return self.client.device_path(self.project, self.cloud_region, self.registry_id, self.device_id)

    def get_num_id(self):
        return str(self.client.get_device(request={"name": self.device_path}).num_id)

    def get(self):
        """
            Grabs the IoT device information stored in the GCP Datastore object
            returns: False if not found, else obj data
        """
        num_id = self.get_num_id()
        if device := self.ds.get():
            return device
        return False

    def check_device(self):
        """ Gets all registered devices and checks if given device exists in project"""
        devices_gen = self.client.list_devices(
            parent=f'projects/{self.project}/locations/{self.cloud_region}/registries/{self.registry_id}')
        device_list = [i.id for i in devices_gen]
        return True if self.device_id in device_list else False

    def msg(self, command, device_type):
        """ Takes input command, encodes it and sends it through the GCP IoT client """
        cmd = self._decode(command, device_type)
        if cmd[0]:
            cmds = []
            for comm in cmd[1]:
                cmds.append(self._msg(comm))
            return cmds[1]
        else:
            return self._msg(command)

    def _msg(self, command):
        data = {"name": self.device_path, "binary_data": command.encode('utf-8')}
        print("[+] Publishing to device topic")
        try:
            self.client.send_command_to_device(
                request=data
            )
        except NotFound as e:
            print(e)
            return False, e
        except Exception as e:
            return False, e
        finally:
            return True, True

    def _decode(self, command, device_type):
        """
        Some commands weren't correctly configured so this method
        will check for any command and then combine both the display and
        the data retrieval as a patch.
        """
        healthcare = ['PATIENT', 'PATIENTS']
        car = ['CAR_USER', 'TRIP', 'BRAKE']
        if command in ['all', 'ALL']:
            if device_type == 4553232:
                commands = self.Commands.BASE + self.Commands.CAR
            elif device_type == 5555555:
                commands = self.Commands.BASE + self.Commands.HEALTHCARE
            else:
                commands = self.Commands.BASE
            device = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=self.device_id).get()
            device['misc'] = commands
            return True, commands
        elif command.upper() in healthcare:
            commands = healthcare
        elif command.upper() == 'IAMSPEED':
            ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=self.device_id)
            device = ds.get()
            device['flag'] = 'CyberArena{HowDoIStopThisThing?}'
            ds.put(device)
            return True, car
        else:
            return False, command
        return True, commands
