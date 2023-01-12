"""
Functions to manage tasks sent to the cloud provider.

This module contains the following classes:
    - CloudOperationsManager: Used, primarily by the instructor, to interact with a unit of escape rooms.
"""
__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

from enum import Enum
from socket import timeout
from googleapiclient import discovery

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.cloud_logger import Logger


class CloudOperationsManager:
    class WaitTypes(Enum):
        ZONE = 0
        REGION = 1
        GLOBAL = 2

    def __init__(self):
        self.logger = Logger("cloud_functions.unit").logger
        self.env = CloudEnv()
        self.service = discovery.build('compute', 'v1')

    def wait_for_completion(self, operation_id, wait_type=WaitTypes.ZONE, wait_seconds=150):
        """

        Args:
            operation_id (int): The operation being waited on
            wait_type (WorkTypes): The type of wait, either zone, region, or global. Defaults to zone
            wait_seconds (int): The number of seconds to wait before returning.

        Returns: True if the operation complete, and False if there is a timeout.

        """
        i = 0
        success = False
        max_wait_iteration = round(wait_seconds / 30)
        while not success and i < max_wait_iteration:
            try:
                self.logger.debug(f"Waiting for operation ID: {operation_id}")
                if wait_type == self.WaitTypes.ZONE:
                    self.service.zoneOperations().wait(project=self.env.project, zone=self.env.zone,
                                                       operation=operation_id).execute()
                elif wait_type == self.WaitTypes.REGION:
                    self.service.regionOperations().wait(project=self.env.project, region=self.env.region,
                                                         operation=operation_id).execute()
                elif wait_type == self.WaitTypes.GLOBAL:
                    self.service.globalOperations().wait(project=self.env.project, operation=operation_id).execute()
                else:
                    raise Exception("Unexpected wait_type in GCP operation wait function.")
                success = True
            except timeout:
                i += 1
                self.logger.warning(f"Response timeout for operation ID: {operation_id}. Trying again")
                pass
        if i >= max_wait_iteration:
            return False
        else:
            return True
