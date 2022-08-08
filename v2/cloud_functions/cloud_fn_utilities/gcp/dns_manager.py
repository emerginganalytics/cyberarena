import ast
import logging

import googleapiclient.discovery
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


class DnsManager:
    def __init__(self):
        self.env = CloudEnv()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.dns = googleapiclient.discovery.build('dns', 'v1')
        log_client = logging_v2.Client()
        log_client.setup_logging()

    def add_dns_record(self, dns_record, server_name):
        response = self.dns.resourceRecordSets().list(project=self.env.project, managedZone=self.env.dnszone,
                                                      name=dns_record).execute()
        existing_rrset = response['rrsets']
        new_ip_address = self._get_external_ip_address(server_name)
        if not new_ip_address:
            logging.error(f"Cannot set the DNS for {dns_record}. The external IP address could not be obtained for "
                          f"{server_name}")
            return
        change_body = {
            "deletions": existing_rrset,
            "additions": [
                {
                    "kind": "dns#resourceRecordSet",
                    "name": dns_record,
                    "rrdatas": [new_ip_address],
                    "type": "A",
                    "ttl": 30
                }
            ],
        }
        # Try first to perform the DNS change, but in case the DNS did not exist, try again without the deletion change.
        try:
            self.dns.changes().create(project=self.env.project, managedZone=self.env.dnszone,
                                      body=change_body).execute()
        except HttpError as e:
            try:
                logging.warning(f"Error in adding DNS record for {dns_record}: {e.error_details}. "
                                f"Attempting to remove the prior deletion.")
                del change_body["deletions"]
                self.dns.changes().create(project=self.env.project, managedZone=self.env.dnszone,
                                          body=change_body).execute()
            except HttpError as e:
                logging.warning(f"Another error when attempting to only add the DNS record {dns_record}: "
                                f"{e.error_details}")

    def delete_dns(self, build_id, ip_address):
        """
        Deletes a DNS record based on the build_id host name and IP address.
        :param build_id: The Datastore entity build_id, which is also the record host name.
        :param ip_address: The IP address of of the record to delete.
        :return: None
        """
        dns_name = build_id + self.env.dns_suffix + "."
        change_body = {"deletions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": dns_name,
                "rrdatas": [ip_address],
                "type": "A",
                "ttl": 30
            },
        ]}
        try:
            self.dns.changes().create(project=self.env.project, managedZone=self.env.dnszone, body=change_body)\
                .execute()
        except HttpError as e:
            logging.error(f"Error when trying to delete DNS for {dns_name}: {e.error_details}")
            raise e

    def add_active_directory_dns(self, build_id, ip_address, network):
        """
        Add a DNS forwarding rule to support an Active Directory server acting as the default DNS server
        @param build_id: The ID of the workout or arena with the DNS server
        @type build_id: String
        @param ip_address: IP address of the active directory server
        @type ip_address: String
        @param network: A list of network names to use for DNS forwarding
        @type network: List
        @return: Status
        @rtype: Boolean
        """

        managed_zone_body = {
            "kind": "dns#managedZone",
            "name": build_id,
            "dnsName": "cybergym.local.",
            "visibility": "private",
            "description": "",
            "privateVisibilityConfig": {
                "kind": "dns#managedZonePrivateVisibilityConfig",
                "networks": []
            },
            "forwardingConfig": {
                "kind": "dns#managedZoneForwardingConfig",
                "targetNameServers": [
                    {
                        "kind": "dns#managedZoneForwardingConfigNameServerTarget",
                        "ipv4Address": ip_address,
                        "forwardingPath": "default"
                    }
                ],
            }
        }

        forwarding_network = {
            "kind": "dns#managedZonePrivateVisibilityConfigNetwork",
            "networkUrl": f"https://www.googleapis.com/compute/v1/projects/{self.env.project}/global/networks/{network}"
        }
        managed_zone_body["privateVisibilityConfig"]["networks"].append(forwarding_network)

        # Try first to perform the DNS change, but in case the DNS did not previously exist, try again without the deletion change.
        try:
            self.dns.managedZones().create(project=self.env.project, body=managed_zone_body).execute()
        except HttpError as e:
            logging.error(f"Error when adding a DNS forwarding rule in Active Directory for {build_id} and network "
                          f"{network}: {e.error_details}")
            raise e

    def delete_active_directory_dns(self, managed_zone):
        """
        Deletes the given managed zone
        @param managed_zone: Managed zone for deleting
        @type managed_zone: str
        @return: Status
        @rtype: bool
        """
        try:
            request = self.dns.managedZones().delete(project=self.env.project, managedZone=managed_zone)
            request.execute()
        except HttpError as e:
            logging.error(f"Error when deleting a DNS forwarding rule for Active Directory on managed zone "
                          f"{managed_zone}: {e.error_details}")
            raise e

    def _get_external_ip_address(self, server_name):
        """
        Provides the IP address of a given server name.
        :param server_name: The server name in the cloud project
        :return: The IP address of the server or throws an error
        """
        try:
            new_instance = self.compute.instances().get(project=self.env.project, zone=self.env.zone,
                                                        instance=server_name).execute()
            ip_address = new_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            return ip_address
        except KeyError:
            logging.error(f"Error: No IP address exists for {server_name}. The server may not be turned on.")
            return False
