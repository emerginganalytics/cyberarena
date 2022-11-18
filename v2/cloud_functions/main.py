import logging
import time
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub
from cloud_fn_utilities.budget_manager import BudgetManager
from handlers.build_handler import BuildHandler
from handlers.maintenance_handler import MaintenanceHandler
from handlers.control_handler import ControlHandler
from handlers.report_handler import ReportHandler
from handlers.agency_handler import AgencyHandler

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

log_client = logging_v2.Client()
log_client.setup_logging()


def cyber_arena_cloud_function(event, context):
    """ Responds to a pub/sub event from other cloud functions to build servers.
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
    bm = BudgetManager()
    if not bm.check_budget():
        logging.error("BUDGET ALERT: Cannot run cloud_fn_build_workout because the budget exceeded variable is set for "
                      "the project")
        return
    handler = event['attributes'].get('handler', None)
    if not handler:
        logging.error(f"No handler provided to cloud function")
        raise ValueError
    else:
        if handler == PubSub.Handlers.BUILD:
            BuildHandler(event['attributes']).route()
        elif handler == PubSub.Handlers.CONTROL:
            ControlHandler(event['attributes']).route()
        elif handler == PubSub.Handlers.MAINTENANCE:
            MaintenanceHandler().route()
        elif handler == PubSub.Handlers.REPORT:
            ReportHandler(event['attributes']).route()
        elif handler == PubSub.Handlers.AGENCY:
            AgencyHandler(event['attributes']).route()
