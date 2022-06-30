import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BudgetManager:
    """
    Handles budget management to avoid cost overruns. A budget_exceeded variable is used in the datastore entity
    admin-info for the project.
    """
    BUDGET_EXCEEDED = "budget_exceeded"

    def __init__(self):
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cybergym')

    def check_budget(self):
        """
        Check whether the budget has been exceeded. If so, cloud functions should not fire.
        @return: Whether the current spending for the month has exceeded the budget.
        @rtype: Boolean
        """
        admin_info = self.datastore_manager.get()
        if self.BUDGET_EXCEEDED not in admin_info:
            admin_info[self.BUDGET_EXCEEDED] = False
            self.datastore_manager.put(admin_info)
            return True
        else:
            budget_exceeded = admin_info[self.BUDGET_EXCEEDED]

        if budget_exceeded:
            return False
        else:
            return True

    def set_budget_exceeded(self, set_value=True):
        """
        Sets the datastore entity variable
        @param set_value:
        @type set_value:
        @return:
        @rtype:
        """
        admin_info = self.datastore_manager.get()
        admin_info[self.BUDGET_EXCEEDED] = set_value
        self.datastore_manager.put(admin_info)
