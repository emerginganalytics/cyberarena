import calendar
import time
from common.dns_functions import delete_dns
from common.globals import parent_project, ArenaWorkoutDeleteType, BUILD_STATES, compute, cloud_log, ds_client, gcp_operation_wait, \
    LOG_LEVELS, LogIDs, project, PUBSUB_TOPICS, region, SERVER_ACTIONS,  WORKOUT_TYPES, zone
from common.start_vm import state_transition
from datetime import datetime
from googleapiclient.errors import HttpError
from google.cloud import datastore


class BudgetManager:
    """
    Handles budget management to avoid cost overruns. A budget_exceeded variable is used in the datastore entity
    admin-info for the project.
    """
    BUDGET_EXCEEDED = "budget_exceeded"

    def __init__(self):
        self.ds_client = datastore.Client(project=parent_project)

    def check_budget(self):
        """
        Check whether the budget has been exceeded. If so, cloud functions should not fire.
        @return: Whether the current spending for the month has exceeded the budget.
        @rtype: Boolean
        """
        admin_info = self.ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
        if self.BUDGET_EXCEEDED not in admin_info:
            admin_info[self.BUDGET_EXCEEDED] = False
            self.ds_client.put(admin_info)
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
        admin_info = self.ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
        admin_info[self.BUDGET_EXCEEDED] = set_value
        self.ds_client.put(admin_info)
