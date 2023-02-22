import googleapiclient.discovery
from google.cloud import logging_v2
from main_app_utilities.gcp.cloud_env import CloudEnv

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ComputeManager:
    """
    Provides ability to pull data on existing compute resources.
    Not intended to manage resource states (start, stop, delete, etc)
    """
    def __init__(self, key_id=None, env_dict=None):
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.key_id = key_id
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()

    def get_snapshots(self):
        response = {'snapshots': [], 'error': ''}
        item_filter = f"name = {self.key_id}*"
        try:
            response['snapshots'] = self.compute.snapshots().list(project=self.env.project,
                                                                  filter=item_filter).execute()
            return response
        except Exception as e:
            response['error'] = e
            return response

    def get_instances(self):
        instance_list = []
        machine_instances = self.compute.instances().list(project=self.env.project, zone=self.env.zone,
                                                          filter=("name:cybergym-*")).execute()
        if 'items' in machine_instances:
            for instance in machine_instances['items']:
                if 'name' in instance:
                    instance_list.append(str(instance['name']))
        return instance_list
