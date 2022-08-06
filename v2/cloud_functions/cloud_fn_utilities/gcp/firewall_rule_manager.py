import time
import googleapiclient.discovery
import logging
from google.cloud import logging_v2
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


class FirewallManager:
    def __init__(self):
        self.env = CloudEnv()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        log_client = logging_v2.Client()
        log_client.setup_logging()

    def build(self, build_id, firewall_spec):
        for rule in firewall_spec:
            # Convert the port specification to the correct json format
            allowed = []
            for port_spec in rule["ports"]:
                protocol, ports = port_spec.split("/")
                if ports == "any":
                    add_ports = {"IPProtocol": protocol}
                else:
                    portlist = ports.split(",")
                    add_ports = {"IPProtocol": protocol, "ports": portlist}
                allowed.append(add_ports)

            firewall_body = {
                "name": f"{build_id}-{rule['name']}",
                "network": f"https://www.googleapis.com/compute/v1/projects/{self.env.project}/global/networks/"
                           f"{build_id}-{rule['network']}",
                "targetTags": rule.get("targetTags", None),
                "allowed": allowed,
                "sourceRanges": rule.get("sourceRanges", None)
            }
            # If targetTags is None, then we do not want to include it in the insertion request
            if not firewall_body["targetTags"]:
                del firewall_body["targetTags"]
            try:
                self.compute.firewalls().insert(project=self.env.project, body=firewall_body).execute()
            except HttpError as err:
                # If the network already exists, then this may be a rebuild and ignore the error
                if err.resp.status in [409]:
                    pass

    def delete(self, build_id, firewall_spec):      # probably does not work but is my best guess
        for rule in firewall_spec:
            # Convert the port specification to the correct json format
            allowed = []
            for port_spec in rule["ports"]:
                protocol, ports = port_spec.split("/")
                if ports == "any":
                    add_ports = {"IPProtocol": protocol}
                else:
                    portlist = ports.split(",")
                    add_ports = {"IPProtocol": protocol, "ports": portlist}
                allowed.append(add_ports)

            firewall_body = {
                "name": f"{build_id}-{rule['name']}",
                "network": f"https://www.googleapis.com/compute/v1/projects/{self.env.project}/global/networks/"
                           f"{build_id}-{rule['network']}",
                "targetTags": rule.get("targetTags", None),
                "allowed": allowed,
                "sourceRanges": rule.get("sourceRanges", None)
            }

            # If targetTags is None, then we do not want to include it in the insertion request
            if not firewall_body["targetTags"]:
                del firewall_body["targetTags"]
            try:
                self.compute.firewalls().delete(project=self.env.project, body=firewall_body).execute()
            except HttpError as err:
                # If the network already exists, then this may be a rebuild and ignore the error
                if err.resp.status in [409]:
                    pass