import time
import googleapiclient.discovery
import logging
from google.cloud import logging_v2
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class VpcManager:
    def __init__(self, build_id, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.build_id = build_id
        log_client = logging_v2.Client()
        log_client.setup_logging()

    def build(self, network_spec):
        network_name = f"{self.build_id}-{network_spec['name']}"
        logging.info(f"Building network {network_name}")
        network_body = {
            "name": network_name,
            "autoCreateSubnetworks": False,
            "region": self.env.region
        }
        try:
            response = self.compute.networks().insert(project=self.env.project, body=network_body).execute()
            self.compute.globalOperations().wait(project=self.env.project, operation=response["id"]).execute()
            time.sleep(3)
        except HttpError as err:
            # If the network already exists, then this may be a rebuild and ignore the error
            if err.resp.status in [409]:
                pass
            else:
                raise err

        for subnet in network_spec['subnets']:
            logging.info(f"Building the subnetwork {network_body['name']}-{subnet['name']}")
            subnetwork_body = {
                "name": f"{network_body['name']}-{subnet['name']}",
                "network": f"projects/{self.env.project}/global/networks/{network_body['name']}",
                "ipCidrRange": subnet['ip_subnet']
            }
            try:
                response = self.compute.subnetworks().insert(project=self.env.project, region=self.env.region,
                                                             body=subnetwork_body).execute()
                self.compute.regionOperations().wait(project=self.env.project, region=self.env.region,
                                                     operation=response["id"]).execute()
            except HttpError as err:
                # If the subnetwork already exists, then this may be a rebuild and ignore the error
                if err.resp.status in [409]:
                    pass
                else:
                    raise err

    def delete(self, network_spec):
        network_name = f"{self.build_id}-{network_spec['name']}"
        for subnet in network_spec['subnets']:
            subnet_name = f"{network_name}-{subnet['name']}"
            logging.info(f"Deleting subnetwork {subnet_name}")
            try:
                response = self.compute.subnetworks().delete(project=self.env.project, region=self.env.region,
                                                             subnetwork=subnet_name).execute()
                wait = self.compute.regionOperations().wait(project=self.env.project, region=self.env.region,
                                                     operation=response["id"]).execute()
            except HttpError as err:
                logging.info(f"Error deleting subnetwork {subnet_name}")
                if err.resp.status in [404]:
                    pass
                else:
                    raise err

        logging.info(f"Deleting network {network_name}")
        try:
            response = self.compute.networks().delete(project=self.env.project, network=network_name).execute()
            wait = self.compute.globalOperations().wait(project=self.env.project, operation=response["id"]).execute()
            if 'error' in wait:
                # error handling
                pass
            time.sleep(3)
        except HttpError as err:
            logging.info(f"Error deleting network {network_name}")
            if err.resp.status in [404]:
                pass
            else:
                raise err
