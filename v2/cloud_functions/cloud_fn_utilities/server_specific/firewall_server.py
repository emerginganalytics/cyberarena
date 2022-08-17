from enum import Enum
import time
from netaddr import IPAddress, IPNetwork
from google.cloud import logging_v2
import logging

from cloud_fn_utilities.globals import DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.state_managers.server_states import ServerStateManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.route_manager import RouteManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FirewallServer:
    def __init__(self, initial_build_id, full_build_spec):
        """
        Creates a firewall server for a given build.
        @param initial_build_id: The build ID used mainly for naming objects in the cloud
        @type initial_build_id: str
        @param full_build_spec: The full build spec needed for identifying network configuration information
        @type full_build_spec: dict
        """
        self.env = CloudEnv()
        self.s = ServerStateManager.States
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.server_spec = None
        self.server_name = None
        self.build_id = initial_build_id
        self.full_build_spec = full_build_spec
        self.firewall_spec = full_build_spec['firewalls']
        # Add the gateway network here for the firewall configurations
        self.full_build_spec['networks'].append(BuildConstants.Networks.GATEWAY_NETWORK_CONFIG)
        self.firewall_spec[0]['networks'].append(BuildConstants.Networks.GATEWAY_NETWORK_NAME)
        self.firewall_server_spec = {}
        self.dst_ranges = {}
        for network in self.full_build_spec['networks']:
            self.dst_ranges[network['name']] = network['subnets'][0]['ip_subnet']

    def build(self):
        for fw in self.firewall_spec:
            firewall_type = fw['type']
            firewall_name = f"{self.build_id}-{fw['name']}"
            self.firewall_server_spec = {
                'parent_id': self.build_id,
                'parent_type': self.build,
                'name': fw['name'],
                'machine_type': BuildConstants.MachineTypes.LARGE.value,
                'can_ip_forward': True,
                'nics': []
            }
            self._add_nics(fw)
            if firewall_type == BuildConstants.Firewalls.VYOS:
                self._add_vyos_features()
            elif firewall_type == BuildConstants.Firewalls.FORTINET:
                self._add_fortinet_features()
            else:
                logging.error(f"Build {self.build_id}: Unsupported firewall type - {firewall_type}.")
                raise
            ds = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=firewall_name)
            ds.put(self.firewall_server_spec)
            ComputeManager(server_name=firewall_name).build()
            self._add_routes(fw)

    def delete(self):
        self._delete_routes()
        for fw in self.firewall_spec:
            firewall_type = fw['type']
            if firewall_type == BuildConstants.Firewalls.FORTINET:
                self._delete_fortinet_features()
            firewall_name = f"{self.build_id}-{fw['name']}"
            ComputeManager(server_name=firewall_name).delete()

    def _add_nics(self, firewall_spec):
        for network in firewall_spec['networks']:
            for network_spec in self.full_build_spec['networks']:
                if network == network_spec['name']:
                    subnet = network_spec['subnets'][0]
                    network_ip = self._get_ip_address(subnet['ip_subnet'])
                    self.firewall_server_spec['nics'].append(
                        {
                            'network': network,
                            'internal_ip': network_ip,
                            'subnet_name': subnet['name'],
                            'external_nat': False
                        }
                    )

    def _get_ip_address(self, subnet):
        taken_ip_addresses = []
        for server in self.full_build_spec['servers']:
            for nic in server['nics']:
                taken_ip_addresses.append(nic['internal_ip'])
        n = IPNetwork(subnet)
        quads = str(n[0]).split(".")
        i = 10
        candidate_ip = None
        for i in range(10, 250, 10):
            candidate_ip = f"{quads[0]}.{quads[1]}.{quads[2]}.{i}"
            if candidate_ip not in taken_ip_addresses:
                continue
        return candidate_ip

    def _add_vyos_features(self):
        self.firewall_server_spec['image'] = FirewallSettings.Vyos.IMAGE
        return

    def _add_fortinet_features(self):
        self.firewall_server_spec['image'] = FirewallSettings.Fortinet.IMAGE
        fortinet_license_server = {
            'build_id': self.build_id,
            'name': 'fortimanager',
            'build_type': BuildConstants.ServerBuildType.MACHINE_IMAGE,
            'machine_type': BuildConstants.MachineTypes.SMALL.value,
            'machine_image': BuildConstants.MachineImages.FORTIMANAGER,
            'nics': [
                {
                    'network': 'gateway',
                    'internal_ip': FirewallSettings.Fortinet.LICENSE_SERVER_IP,
                    'subnet_name': 'default',
                    'external_nat': False
                }
            ]
        }
        fortinet_server_name = f"{self.build_id}-{fortinet_license_server['name']}"
        ds = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=fortinet_server_name)
        ds.put(fortinet_license_server)
        ComputeManager(server_name=fortinet_server_name).build()

    def _delete_fortinet_features(self):
        fortinet_server_name = f"{self.build_id}-fortimanager"
        ComputeManager(server_name=fortinet_server_name).delete()

    def _add_routes(self, firewall_spec):
        routes = []
        for network in firewall_spec['networks']:
            if network != BuildConstants.Networks.GATEWAY_NETWORK_NAME:
                new_route = {
                    'name': f"default-{network}-through-firewall",
                    'network': network,
                    'dest_range': '0.0.0.0/0',
                    'next_hop_instance': self.firewall_server_spec['name']
                }
                routes.append(new_route)
            for to_network in firewall_spec['networks']:
                if to_network != network:
                    new_route = {
                        'name': f"default-{network}-to-{to_network}",
                        'network': network,
                        'dest_range': self.dst_ranges[to_network],
                        'next_hop_instance': self.firewall_server_spec['name']
                    }
                    routes.append(new_route)
        rm = RouteManager(self.build_id)
        rm.build(routes)

    def _delete_routes(self):
        rm = RouteManager(self.build_id)
        rm.delete()

    # def _wait_for_deletion(self):
    #     i = 0
    #     success = False
    #     while not success and i < 5:
    #         result = compute.firewalls().list(project=project, filter=f"name = {self.build_id}*").execute()

class FirewallSettings:
    class Vyos:
        IMAGE = "image-cyberarena-vyos"

    class Fortinet:
        IMAGE = "image-cybergymfortinet-cybergym-fortinet-fortigate"
        LICENSE_SERVER_IP = '10.1.0.100'
