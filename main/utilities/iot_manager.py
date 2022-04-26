import google.api_core.exceptions
from google.cloud import iot_v1, datastore
from google.protobuf import field_mask_pb2 as gp_field_mask
from utilities.globals import ds_client, project, log_client, LOG_LEVELS

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class IotManager(object):
    def __init__(self):
        self.cloud_region = 'us-central1'
        self.registry_id = 'cybergym-registry'
        self.parent_path = f'projects/{project}/locations/{self.cloud_region}/registries/{self.registry_id}'
        self.kind = 'cybergym-iot-device'  # target datastore kind name
        self.iot_client = iot_v1.DeviceManagerClient()

    class DeviceStates:
        READY = 'READY'
        SENT = 'SENT'
        CHECK = 'CHECK'
        UPDATE = 'UPDATE'

    class APIActions:
        REGISTER = 'REGISTER'
        DELETE = 'DELETE'
        UPDATE = 'UPDATE'
        TEST = 'TEST'

    def get_iot_device(self, device_id):
        """Sends request to IoT core to retrieve information on a single device."""
        device_path = self.iot_client.device_path(project, self.cloud_region, self.registry_id, device_id)
        device = self.iot_client.get_device(request={"name": device_path})
        return device.id

    def get_all_registered_iot(self):
        """
        Sends request to IoT core API to pull list of all current registered IoT devices on the
        current project.

        Used in cases where devices were created manually
        :return: List of registered IoT devices
        """
        parent_path = f'projects/{project}/locations/{self.cloud_region}/registries/{self.registry_id}'
        devices_gen = self.iot_client.list_devices(parent=parent_path)

        devices = []
        for device in devices_gen:
            device_path = self.iot_client.device_path(project, self.cloud_region, self.registry_id, device.id)
            devices.append(self.iot_client.get_device(request={"name": device_path}))
        return devices

    def create_all_iot_device_entity(self):
        """
        Parses registered IoT device list and sends call to add to datastore.

        Used for cases where devices were created manually before datastore Kind was created
        """
        devices = self.get_all_registered_iot()
        for device in devices:
            self.add_device_to_datastore(device_id=device.id)

    def add_device_to_datastore(self, device_id):
        """
        Takes device information and creates an associated datastore entity
        :param device_id
        """
        new_device = datastore.Entity(ds_client.key(self.kind, device_id))
        new_device['device_id'] = device_id
        new_device['status'] = self.DeviceStates.READY
        new_device['comments'] = ''
        new_device['current_student'] = {'name': '', 'address': '', 'tracking_number': ''}
        new_device['date_sent'] = ''
        new_device['date_received'] = ''
        new_device['device_url'] = f"https://console.cloud.google.com/iot/locations/" \
                                   f"{self.cloud_region}/registries/{self.registry_id}/" \
                                   f"devices/details/{device_id}"
        ds_client.put(new_device)

    def update_device_entity(self, device_id, data):
        """
        Updates fields in device datastore object

        The data object must include a status value and a
        combination of the following key value pairs:
        :param data: {
            'comments': '',
            'current_student': {'name': '', 'address': '', 'tracking_number': ''},
            'date_received': (timestamp, None),
            'date_sent': (timestamp, None),
            'status': self.IotDeviceStates; REQUIRED,
        }
        :param device_id: str()
        """
        # Get device datastore object
        if self.check_device_id(device_id):
            device_ds = ds_client.get(ds_client.key(self.kind, device_id))

            # Parse sent data
            comments = data.get('comments', None)
            current_student = data.get('current_student', None)
            date_recv = data.get('date_received', None)
            date_sent = data.get('date_sent', None)
            status = data.get('status', None)
            certificate = data.get('certificate', None)

            # Fields are updated based on device status
            if status:
                if status == self.DeviceStates.SENT:
                    device_ds['status'] = status
                    # Device was assigned to and sent to a new student
                    device_ds['date_sent'] = date_sent
                    device_ds['current_student'] = current_student

                    # These values should be reset upon each new assigned student
                    device_ds['date_received'] = 'N/A'
                    device_ds['comments'] = comments
                elif status == self.DeviceStates.CHECK:
                    # Device was received but needs to be checked before being sent out again
                    device_ds['status'] = status
                    device_ds['date_received'] = date_recv
                    device_ds['comments'] = comments
                elif status == self.DeviceStates.READY:
                    print(comments)
                    # Device has passed check state and is ready to be used again
                    device_ds['current_student'] = {'name': "N/A", "address": "N/A", 'tracking_number': 'N/A'}
                    device_ds['date_sent'] = 'N/A'
                    device_ds['status'] = status
                    device_ds['comments'] = comments
                elif status == self.DeviceStates.UPDATE:
                    # Device registered ssh public key needs to be updated
                    update_cert = self.update_iot_device_key(device_id=device_id, certificate=certificate)
                    if update_cert['status'] != 200:
                        return update_cert
                    device_ds['status'] = status
                    device_ds['comments'] = comments
                ds_client.put(device_ds)
                return self.DeviceAPIStatus(device_id=device_id, status=200, action=self.APIActions.UPDATE).__dict__()

    def check_device_id(self, device_id):
        """Checks for existing device_id in registered IoT devices"""
        for device in self.get_all_registered_iot():
            if device_id == device.id:
                return True
        return False

    def register_new_iot_device(self, device_id, certificate):
        """
        Creates and registers a new IoT device to the IoT core and
        before adding it to the datastore

        :parameter certificate: public key passed as a string
        :parameter device_id

        :return: str or json dict
        """
        if not self.check_device_id(device_id):
            parent = self.iot_client.registry_path(project, self.cloud_region, self.registry_id)

            device_template = {
                "id": device_id,
                "credentials": [
                    {
                        'public_key': {
                            'format': iot_v1.PublicKeyFormat.RSA_X509_PEM,
                            'key': certificate,
                        },
                    }
                ],
            }
            try:
                # Register new device with IoT core
                self.iot_client.create_device(request={'parent': parent, 'device': device_template})

                # Add new device to datastore if it doesn't already exist
                self.add_device_to_datastore(self.get_iot_device(device_id))
                return self.DeviceAPIStatus(device_id=device_id, status=200, action=self.APIActions.REGISTER).__dict__()
            except google.api_core.exceptions.InvalidArgument as e:
                return self.DeviceAPIStatus(device_id=device_id, status=400, action=self.APIActions.REGISTER, err=e).__dict__()
            except google.api_core.exceptions.GoogleAPIError as e:
                return self.DeviceAPIStatus(device_id=device_id, status=405, action=self.APIActions.REGISTER, err=e).__dict__()
        return self.DeviceAPIStatus(device_id=device_id, status=405, action=self.APIActions.REGISTER,
                                    err='Device already exists in project').__dict__()

    def update_iot_device_key(self, device_id, certificate):
        """Update existing device SSH keys"""
        # load new certificate
        key = iot_v1.PublicKeyCredential(
            format=iot_v1.PublicKeyFormat.RSA_X509_PEM, key=certificate
        )
        cred = iot_v1.DeviceCredential(public_key=key)

        # get device we want to update
        device_path = self.iot_client.device_path(project, self.cloud_region, self.registry_id, device_id)
        device = self.iot_client.get_device(request={"name": device_path})

        # select which key to update and assign it the new value
        device.id = b""
        device.num_id = 0
        device.credentials[0] = cred
        mask = gp_field_mask.FieldMask()
        mask.paths.append("credentials")

        # send update request
        self.iot_client.update_device(request={"device": device, "update_mask": mask})
        return self.DeviceAPIStatus(device_id=device_id, status=200, action=self.APIActions.UPDATE).__dict__()

    def delete_iot_device(self, device_id):
        """Removes device from IoT core and datastore"""
        if self.check_device_id(device_id):
            # Delete device from IoT core
            device_path = self.iot_client.device_path(project, self.cloud_region, self.registry_id, device_id)
            self.iot_client.delete_device(request={'name': device_path})

            #  Delete device from Datastore
            device_key = ds_client.key(self.kind, device_id)
            ds_client.delete(device_key)
            return self.DeviceAPIStatus(device_id=device_id, status=200, action=self.APIActions.DELETE).__dict__()
        return self.DeviceAPIStatus(device_id=device_id, status=404, action=self.APIActions.DELETE).__dict__()

    def send_command(self, device_id, command=None):
        """Sends an arbitrary command to device to check for a valid connection"""
        device_path = self.iot_client.device_path(project, self.cloud_region, self.registry_id, device_id)
        if not command:
            command = 'red'
        data = command.encode('utf-8')
        try:
            result = self.iot_client.send_command_to_device(request={"name": device_path, "binary_data": data})
            return self.DeviceAPIStatus(device_id=device_id, status=200, action=self.APIActions.TEST).__dict__()
        except google.api_core.exceptions.NotFound as e:
            return self.DeviceAPIStatus(device_id=device_id, status=404, action=self.APIActions.TEST, err=e).__dict__()
        except google.api_core.exceptions.FailedPrecondition as e:
            return self.DeviceAPIStatus(device_id=device_id, status=400, action=self.APIActions.TEST, err=e).__dict__()
        except:
            return self.DeviceAPIStatus(device_id=device_id, status=405, action=self.APIActions.TEST,
                                        err='Undefined error caught during connection test').__dict__()

    class DeviceAPIStatus:
        """
        Class used to build helpful context based messages
        """
        def __init__(self, device_id, status, action, err=None):
            self.device_id = device_id
            self.status = status
            self.action = action
            self.err = err
            self.messages = {
                200: f'Action {self.action} succeeded for device, {self.device_id}: error: {self.err}',
                400: f'Action {self.action} failed for device, {self.device_id}: error: {self.err}',
                404: f'Action {self.action} failed for device, {self.device_id}: error: Device not found',
                405: f'Action {self.action} failed for device, {self.device_id}: error: {self.err}'
            }

        def __repr__(self):
            if self.status in self.messages:
                return {'status': self.status, 'message': self.messages[self.status], 'error': self.err}
            return {'status': self.status, 'message': self.err, 'error': self.err}

        def __dict__(self):
            if self.status in self.messages:
                return {'status': self.status, 'message': self.messages[self.status], 'error': str(self.err)}
            return {'status': self.status, 'message': str(self.err), 'error': str(self.err)}

# [ eof ]
