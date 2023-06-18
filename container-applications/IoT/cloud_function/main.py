import logging
from google.cloud import logging_v2

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
        raise ValueError
    if 'maintenance' in event['attributes']:
        IotCloudMaintenance(attributes=event['attributes']).maintenance()
    else:
        device_num_id = event['attributes'].get('deviceNumId')
        if not device_num_id:
            logging.error(f"No device number id provided to cloud function")
            raise ValueError
        else:
            IotCloudMaintenance(attributes=event['attributes'], dataflow=event['data']).msg()

