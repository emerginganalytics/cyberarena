import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.reports.attack_report import AttackReport


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ReportHandler:
    def __init__(self, event_attributes):
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        self.report_type = self.event_attributes.get('report_type', None)
        if not self.report_type:
            raise AttributeError('Missing attr report_type in request')

    def route(self):
        if self.report_type == PubSub.Reports.ATTACK:
            AttackReport(self.event_attributes, env_dict=self.env.get_env())

# [ eof ]
