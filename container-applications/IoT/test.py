from app_utilities.globals import DatastoreKeyTypes, BuildConstants, PubSub, get_current_timestamp_utc
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.gcp.iot_manager import IotManager
from cloud_function.iot_maintenance import IotCloudMaintenance
from cloud_function.main import iot_device_cloud_function
from setup import IoTApp

if __name__ == '__main__':
    event = {
        '@type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage',
        'attributes': {
            'deviceId': 'cybergym-raspbpi3',
            'deviceNumId': '2758193955719052',
            'deviceRegistryId': 'cybergym-registry',
            'deviceRegistryLocation': 'us-central1',
            'projectId': 'ualr-cybersecurity', 'subFolder': ''
        },
        'data': 'eyJ0cyI6IDE2ODcwNTc4MjksICJzZW5zb3JfZGF0YSI6IHsidGVtcCI6ICI5Mi4xOGYiLCAiaHVtaWRpdHkiOiAiNjcuMTElIiwgInByZXNzdXJlIjogIjk5Ni40NyBtYmFyIiwgIngiOiAzNTcuOTQsICJ5IjogOC40LCAieiI6IDAuMCwgImhlYXJ0IjogIjY3IGJwbSIsICJmbGFnIjogIiIsICJjb2xvciI6ICIiLCAiY2FyIjogeyJ2ZWhpY2xlIjogIiIsICJ0cmlwIjogIiIsICJwcm9kdWN0cyI6ICIiLCAidXNlciI6ICIifSwgInBhdGllbnRzIjogIiJ9LCAic3lzdGVtIjogeyJtZW1vcnkiOiAiMjQuNyIsICJpcCI6ICIyMDYuMjU1LjQ4LjgzIiwgInN0b3JhZ2UiOiAiNTkuOCJ9fQ=='
    }
    IotCloudMaintenance(attributes=event['attributes'], dataflow=event['data']).maintenance()

