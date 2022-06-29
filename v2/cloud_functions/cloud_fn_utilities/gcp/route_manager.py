import time
import googleapiclient.discovery
import logging
from google.cloud import logging_v2
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class RouteManager:
    def __init__(self, build_id):
        self.env = CloudEnv()
        self.build_id = build_id
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        log_client = logging_v2.Client()
        log_client.setup_logging()

    def build(self, routing_spec):
        for route in routing_spec:
            next_hop_instance = f"https://www.googleapis.com/compute/v1/projects/{self.env.project}/zones/{self.env.zone}" \
                                f"/instances/{self.build_id}-{route['next_hop_instance']}"
            route_body = {
                "destRange": route["dest_range"],
                "name": f"{self.build_id}-{route['name']}",
                "network": f"https://www.googleapis.com/compute/v1/projects/{self.env.project}/global/networks/"
                           f"{self.build_id}-{route['network']}",
                "priority": 0,
                "tags": [],
                "nextHopInstance": next_hop_instance
            }
            self.compute.routes().insert(project=self.env.project, body=route_body).execute()
