from enum import Enum
import time
from socket import timeout
import googleapiclient.discovery
import logging
from google.cloud import logging_v2
from googleapiclient.errors import HttpError
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

from cloud_fn_utilities.globals import DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.dns_manager import DnsManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager, ServerStates
from cloud_fn_utilities.state_managers.server_states import ServerStateManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Bryce Ebsen, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ComputeManager:
    GOOGLE_MACHINE_TYPES = ['e2-micro', 'e2-medium', 'e2-standard-2', 'e2-standard-4', 'e2-standard-8', 'e2-standard-4']

    MAX_TIMEOUT_ITERATIONS = 5
    SERVICE_ACCOUNT_CONFIG = [{
        'email': 'default',
        'scopes': [
            'https://www.googleapis.com/auth/devstorage.read_write',
            'https://www.googleapis.com/auth/logging.write'
        ]
    }]

    def __init__(self, server_name):
        self.env = CloudEnv()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.dns_manager = DnsManager()
        self.s = ServerStates
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.server_name = server_name
        self.server_spec = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.server_name).get()
        if not self.server_spec:
            logging.error(f"No record exists for compute record {server_name}")
            raise LookupError
        self.state_manager = ServerStateManager(initial_build_id=self.server_name)

    def build(self):
        """
        Builds an individual server based on the specification in the Datastore entity with name server_name.
        :param server_spec: specification of the server to build
        :param build_id: ID of the build used for the predicate
        :return: A boolean status on the success of the build
        """

        self.state_manager.state_transition(self.s.BUILDING)
        self._add_disks()
        self._add_metadata()
        self._add_nics()
        machine_type = self._lookup_machine_type(self.server_spec.get('machine_type',
                                                                      BuildConstants.MachineTypes.SMALL.value))
        config = {
            'name': self.server_name,
            'machineType': f"zones/{self.env.zone}/machineTypes/{machine_type}",
            'tags': self.server_spec.get('server_tags', None),
            'disks': self.server_spec.get('disks', None),
            'metadata': self.server_spec.get('metadata', None),
            'canIpForward': self.server_spec.get('can_ip_forward', None),
            'networkInterfaces': self.server_spec.get('network_interfaces', None),
            'serviceAccounts': self.SERVICE_ACCOUNT_CONFIG,
            'minCpuPlatform': self.server_spec.get('min_cpu_platform', None)
        }

        if self.server_spec.get('build_type', None) == BuildConstants.ServerBuildType.MACHINE_IMAGE:
            source_machine_image = f"projects/{self.env.project}/global/machineImages/" \
                                   f"{self.server_spec['machine_image']}"
            try:
                response = self.compute.instances().insert(project=self.env.project, zone=self.env.zone, body=config,
                                                           sourceMachineImage=source_machine_image).execute()
            except HttpError as err:
                if err.resp.status in [409]:
                    logging.warning(f"The server {self.server_name} already exists.")
                    return
        else:
            if "delayed_start" in self.server_spec and self.server_spec["delayed_start"]:
                time.sleep(30)
            try:
                response = self.compute.instances().insert(project=self.env.project, zone=self.env.zone,
                                                           body=config).execute()
            except HttpError as err:
                if err.resp.status in [409]:
                    logging.warning(f"The server {self.server_name} already exists.")
                    return
                else:
                    raise err
        logging.info(f'Sent job to build {self.server_name}, and waiting for response')
        i = 0
        success = False
        while not success and i < self.MAX_TIMEOUT_ITERATIONS:
            try:
                self.compute.zoneOperations().wait(project=self.env.project, zone=self.env.zone,
                                                   operation=response["id"]).execute()
                success = True
            except timeout:
                i += 1
                logging.warning(f"Response timeout {i} of {self.MAX_TIMEOUT_ITERATIONS} for build on server "
                                f"{self.server_name}.")
                pass

        if success:
            logging.info(f'Successfully built server {self.server_name}!')
            self.state_manager.state_transition(self.s.RUNNING)
        else:
            logging.error(f'Timeout in trying to build server {self.server_name}')
            self.state_manager.state_transition(self.s.BROKEN)
            raise ConnectionError

        # If the server is an external proxy, then register its DNS name
        dns_hostname = self.server_spec.get('dns_hostname', None)
        if dns_hostname:
            dns_record = dns_hostname + self.env.dns_suffix + "."
            self.dns_manager.add_dns_record(dns_record, self.server_name)

        # Now stop the server before completing
        logging.info(f'Stopping {self.server_name}')
        self.compute.instances().stop(project=self.env.project, zone=self.env.zone, instance=self.server_name).execute()
        self.state_manager.state_transition(self.s.STOPPED)

    def start(self):
        """
        Starts a server based on the specification in the Datastore entity with name server_name. A guacamole server
        is also registered with DNS.
        """
        self.state_manager.state_transition(self.s.STARTING)
        i = 0
        start_success = False
        while not start_success and i < 5:
            try:
                if "delayed_start" in self.server_spec and self.server_spec["delayed_start"]:
                    time.sleep(30)
                response = self.compute.instances().start(project=self.env.project, zone=self.env.zone,
                                                          instance=self.server_name).execute()
                start_success = True
                logging.info(f'Sent job to start {self.server_name}, and waiting for response')
            except BrokenPipeError:
                i += 1
        self._wait_to_finish(response['id'])

        # If the server is an external proxy, then register its DNS name
        dns_hostname = self.server_spec.get('dns_hostname', None)
        if dns_hostname:
            dns_record = dns_hostname + self.env.dns_suffix + "."
            self.dns_manager.add_dns_record(dns_record, self.server_name)

        self.state_manager.state_transition(self.s.RUNNING)
        logging.info(f"Finished starting {self.server_name}")

    def stop(self):
        """
        Stops a server based on the specification in the Datastore entity with name server_name.
        """
        if self.state_manager.get_state() != self.s.STOPPED.value:
            self.state_manager.state_transition(self.s.STOPPING)
            i = 0
            stop_success = False
            while not stop_success and i < 5:
                try:
                    response = self.compute.instances().stop(project=self.env.project, zone=self.env.zone,
                                                             instance=self.server_name).execute()
                    stop_success = True
                    logging.info(f'Sent job to stop {self.server_name}, and waiting for response')
                except BrokenPipeError:
                    i += 1
            self._wait_to_finish(response['id'])

            self.state_manager.state_transition(self.s.STOPPED)
            logging.info(f"Finished stopping {self.server_name}")
        else:
            logging.info(f"Server {self.server_name} is not running")

    def nuke(self):
        """
        Deletes a server based on the specification in the Datastore entity with the name server_name. Then rebuilds
        the server.
        """
        self.delete()
        self.build()

    def delete(self):
        """
        Deletes a server based on the specification in the Datastore entity with the name server_name.
        """
        self.state_manager.state_transition(self.s.DELETING)

        logging.info(f'Deleting {self.server_name}')
        try:
            response = self.compute.instances().delete(project=self.env.project, zone=self.env.zone,
                                                       instance=self.server_name).execute()
        except HttpError as err:
            if err.resp.status in [404]:
                self.state_manager.state_transition(self.s.DELETED)
                return
        self._wait_to_finish(response['id'])

    def _add_disks(self):
        disks = None
        if self.server_spec.get('build_type', None) != BuildConstants.ServerBuildType.MACHINE_IMAGE:
            try:
                image_response = self.compute.images()\
                    .get(project=self.env.project, image=self.server_spec['image']).execute()
            except errors.HttpError as err:
                # Something went wrong, print out some information.
                print('There was an error creating the model. Check the details:')
                print(err._get_reason())
            image = image_response['selfLink']
            disks = [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': image,
                    }
                }
            ]

            add_disk = self.server_spec.get('add_disk', 0)
            if add_disk != 0:
                new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
                            "source":
                                f"projects/{self.env.project}/zones/{self.env.zone}/disks/{self.server_name}-disk"}
                disks.append(new_disk)
                # Now build the disk so it's ready to attach when the server is built.
                try:
                    image_config = {"name": self.server_name + "-disk", "sizeGb": add_disk,
                                    "type": f"projects/{self.env.project}/zones/{self.env.zone}/diskTypes/pd-ssd"}
                    response = self.compute.disks().insert(project=self.env.project, zone=self.env.zone,
                                                           body=image_config).execute()
                    self.compute.zoneOperations().wait(project=self.env.project, zone=self.env.zone,
                                                       operation=response["id"]).execute()
                except HttpError as err:
                    if err.resp.status in [409]:
                        pass
        self.server_spec['disks'] = disks

    def _add_metadata(self):
        """
        A config can have metadata items, and we keep the ssh-key as a separate field to make the config easier to
        understand, develop, and maintain.
        """
        metadata = {'items': []}
        if self.server_spec.get('metdata', None):
            metadata['items'].append(self.server_spec['metadata'])
        if self.server_spec.get('sshkey', None):
            metadata['items'].append({"key": "ssh-keys", "value": self.server_spec['sshkey']})
        if self.server_spec.get('guacamole_startup_script', None):
            metadata['items'].append({"key": "startup-script", "value": self.server_spec['guacamole_startup_script']})
        self.server_spec['metadata'] = metadata

    def _add_nics(self):
        network_prefix = self.server_spec.get('fixed_arena_id', self.server_spec['parent_id'])
        network_interfaces = []
        for network in self.server_spec['nics']:
            if network.get("external_nat", None):
                accessConfigs = {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            else:
                accessConfigs = None
            add_network_interface = {
                'network': f'projects/{self.env.project}/global/networks/{network_prefix}-{network["network"]}',
                'subnetwork': f'regions/{self.env.region}/subnetworks/'
                              f'{network_prefix}-{network["network"]}-{network["subnet_name"]}',
                'accessConfigs': [
                    accessConfigs
                ]
            }
            if 'internal_ip' in network:
                add_network_interface['networkIP'] = network["internal_ip"]

            if 'alias_ip_ranges' in network:
                add_network_interface['aliasIpRanges'] = network['alias_ip_ranges']
            network_interfaces.append(add_network_interface)
        self.server_spec['network_interfaces'] = network_interfaces

    def _wait_to_finish(self, response_id):
        i = 0
        success = False
        while not success and i < 5:
            try:
                self.compute.zoneOperations().wait(project=self.env.project, zone=self.env.zone,
                                                   operation=response_id).execute()
                success = True
            except timeout:
                i += 1
                logging.warning(f'Response timeout for stopping server {self.server_name}. Trying again')
                pass
        if not success:
            logging.error(f'Timeout in operation on server {self.server_name}')
            self.state_manager.state_transition(self.s.BROKEN)
            raise ConnectionError

    @staticmethod
    def _lookup_machine_type(machine_type):
        if type(machine_type) == int and machine_type in range(len(ComputeManager.GOOGLE_MACHINE_TYPES)):
            return ComputeManager.GOOGLE_MACHINE_TYPES[machine_type]
        for mt in BuildConstants.MachineTypes:
            if machine_type == mt.name:
                return ComputeManager.GOOGLE_MACHINE_TYPES[mt.value]
        return machine_type
