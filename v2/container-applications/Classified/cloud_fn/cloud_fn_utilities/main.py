import logging
from google.cloud import logging_v2

from cloud_fn_utilities.iot.exceptions import MissingAttributes, MissingData, InvalidAction
from cloud_fn_utilities.iot.iot_manager import IotManager
from cloud_fn_utilities.iot.mqtt_handler import MqttHandler
from cloud_fn_utilities.globals import PubSub
from iot_maintenance import IotCloudMaintenance


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

log_client = logging_v2.Client()
log_client.setup_logging()


def iot_device_cloud_function(event, context):
    """
    Responds to a pub/sub event from other cloud functions to build servers.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    print(event)
    if 'attributes' not in event:
        logging.error(f"No attributes provided to the cloud function")
        raise MissingAttributes(f"No attributes provided to the cloud function")

    attributes = event['attributes']
    device_id = attributes.get('device_id', None)
    action = attributes.get('action', PubSub.IotActions.CONTROL.value)
    data = event.get('data', None)
    if not device_id:
        logging.error(f'No device_id provided to cloud function for action {action}')
        raise MissingAttributes(f'No device_id provided to cloud function for action {action}')
    else:
        if action == PubSub.IotActions.CONTROL.value:
            if not data:
                raise MissingData(f'Missing command data for action {action}')
            IotManager(device_id=device_id, attributes=attributes, dataflow=event['data']).route()
        elif action == PubSub.IotActions.POLL.value:
            MqttHandler(device_id=device_id).poll()
        elif action == PubSub.IotActions.MAINTENANCE.value:
            IotCloudMaintenance(attributes=event['attributes'], dataflow=event['data']).msg()
        else:
            raise InvalidAction(f'Unrecognized action with value {action}')


# [ eof ]
