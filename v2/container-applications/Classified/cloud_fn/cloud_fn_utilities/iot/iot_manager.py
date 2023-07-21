from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes


class IotManager:
    def __init__(self, device_id=None, attributes=None, dataflow=None):
        self.device_id = device_id
        self.attributes = attributes
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.IOT_DEVICE.value, key_id=self.device_id)

    def route(self):
        pass

    def _clean_records(self):
        pass
