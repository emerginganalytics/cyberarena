from enum import Enum
import time
import string
import random
from netaddr import IPAddress, IPNetwork
from google.cloud import logging_v2
import logging

from cloud_fn_utilities.globals import DatastoreKeyTypes, BuildConstants, PubSub
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.state_managers.server_states import ServerStateManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.server_specific.guacamole_configuration import GuacamoleConfiguration

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class DisplayProxy:
    def __init__(self, build_id, build_spec):
        """
        Creates a guacamole server with the configured connections for proxying servers used for displays
        @param build_id: The build ID used mainly for naming objects in the cloud
        @type build_id: str
        @param build_spec: The full build spec
        @type build_spec: DatastoreEntity
        """
        self.env = CloudEnv()
        self.server_name = f"{build_id}-display-guacamole-server"
        self.s = ServerStateManager
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.server_spec = None
        self.build_id = build_id
        self.build_spec = build_spec
        self.server_specs = build_spec['servers']
        self.guac_connections = []
        self.ds = DataStoreManager()
        self.guac = GuacamoleConfiguration(self.build_id)

    def build(self):
        build_ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA, key_id=self.build_id)
        build_record = build_ds.get()
        proxy_configs = []
        proxy_connections = []
        for server in self.server_specs:
            human_interaction = server.get('human_interaction', None)
            if human_interaction:
                for connection in human_interaction:
                    if connection.get('display', False):
                        server_ip = server['nics'][0]['internal_ip']
                        proxy_config = self.guac.prepare_guac_connection(connection=connection, server_ip=server_ip)
                        proxy_configs.append(proxy_config)
                        connection = {
                            'server': server['name'],
                            'internal_ip_address': server_ip,
                            'username': proxy_config['workspace_username'],
                            'password': proxy_config['workspace_password']
                        }
                        proxy_connections.append(connection)

        build_record['proxy_connections'] = proxy_connections
        build_ds.put(build_record)

        guac_startup_script = self.guac.get_guac_startup_script(proxy_configs)
        server_spec = {
            'parent_id': self.build_id,
            'name': self.server_name,
            'image': BuildConstants.MachineImages.GUACAMOLE,
            'tags': {'items': ['student-entry']},
            'machine_type': BuildConstants.MachineTypes.SMALL.value,
            'nics': [
                {
                    "network": BuildConstants.Networks.GATEWAY_NETWORK_NAME,
                    "subnet_name": "default",
                    "external_nat": True,
                    "internal_ip": BuildConstants.Networks.Reservations.DISPLAY_SERVER
                }
            ],
            'build_type': BuildConstants.BuildType.FIXED_ARENA,
            'dns_hostname': f"{self.build_id}-display",
            'guacamole_startup_script': guac_startup_script
        }
        self.ds.put(server_spec, key_type=DatastoreKeyTypes.SERVER, key_id=self.server_name)
        ComputeManager(server_name=self.server_name).build()
