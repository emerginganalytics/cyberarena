from google.api_core.exceptions import NotFound
from google.cloud import iot_v1

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes


class IotManager:
    """
    Managing class to handle Publish messages used by Cloud Run container
    """
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.env = CloudEnv()
        self.project = self.env.project
        self.cloud_region = 'us-central1'
        self.registry_id = 'cybergym-registry'
        self.client = iot_v1.DeviceManagerClient()
        if self.device_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE, key_id=device_id)
            self.device_path = self._set_path()

    def _set_path(self):
        return self.client.device_path(self.project, self.cloud_region, self.registry_id, self.device_id)

    def get_num_id(self):
        return str(self.client.get_device(request={"name": self.device_path}).num_id)

    def get_by_num_id(self, num_id):
        parent_path = f'projects/{self.env.project}/locations/{self.cloud_region}/registries/{self.registry_id}'
        devices_gen = self.client.list_devices(parent=parent_path)
        for device in devices_gen:
            if device.num_id == num_id:
                device_path = self.client.device_path(self.project, self.cloud_region, self.registry_id, device.id)
                return self.client.get_device(request={"name": device_path})
        return False

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

    def msg(self, command):
        """ Takes input command, encodes it and sends it through the GCP IoT client """
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
