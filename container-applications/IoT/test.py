from app_utilities.globals import DatastoreKeyTypes, BuildConstants, PubSub, get_current_timestamp_utc, Commands, Tokens
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.gcp.cloud_env import CloudEnv
# from app_utilities.gcp.iot_manager import IotManager
from cloud_function.iot_maintenance import IotCloudMaintenance
from cloud_function.main import iot_device_cloud_function

if __name__ == '__main__':
    IotCloudMaintenance()._reset_records()
    #Tokens.token_by_uid(Tokens.GUEST)
