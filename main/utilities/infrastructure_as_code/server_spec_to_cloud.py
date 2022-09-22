"""
Parses a given workout or arena build and creates new server specs in the datastore. These specs are cloud-ready and
will be called on later by cloud functions when the build is ready to process.
"""

import time
import random
import string
from datetime import datetime
import calendar
from google.cloud import datastore
from netaddr import IPAddress, IPNetwork
from marshmallow import Schema, fields, ValidationError
from utilities.globals import ds_client, workout_globals, dns_suffix, LOG_LEVELS, BUILD_STATES, cloud_log, LogIDs, \
    BuildTypes, zone, ComputeBuildTypes, compute, project


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class ServerSpecToCloud:
    def __init__(self, server_spec, build_id, startup_scripts=None, student_entry=False, options=None):
        """
        Initialize the server specification from a build specification.
        @param server_spec: The raw build specification for the server.
        @type server_spec: dict
        @param build_id: The ID associated with the build
        @type build_id: str
        @param startup_scripts: The startup scripts for all servers associated with this build
        @type startup_scripts: dict
        @param student_entry: Whether this is a student entry server
        @type: bool
        @param options: Additional options to include with the server
        @type options: dict
        """
        base_name = server_spec['name']
        self.server_name = f"{build_id}-{base_name}"
        # First check to see if the server configuration already exists. If so, then return without error
        exists_check = ds_client.query(kind='cybergym-server')
        exists_check.add_filter("name", "=", self.server_name)
        if len(list(exists_check.fetch())) > 0:
            cloud_log(LogIDs.MAIN_APP, f"The server {self.server_name} already exists. Skipping configuration.",
                      LOG_LEVELS.ERROR)
            raise ValueError
        self.build_id = build_id
        self.custom_image = server_spec.get('image', None)
        self.build_type = server_spec.get("build_type", None)
        self.machine_image = server_spec.get("machine_image", None)
        self.sshkey = server_spec.get("sshkey", None)
        self.tags = server_spec.get('tags', None)
        self.machine_type = server_spec.get("machine_type", "n1-standard-1")
        self.network_routing = server_spec.get("network_routing", None)
        self.min_cpu_platform = server_spec.get("minCpuPlatform", None)
        self.add_disk = server_spec.get("add_disk", None)
        self.options = server_spec.get("options", None)
        self.snapshot = server_spec.get('snapshot', None)
        self.nested_vm = server_spec.get('nested_virtualization', False)

        # Add the network configuration
        self.networks = []
        self.dns = None
        for n in server_spec['nics']:
            n['external_NAT'] = n['external_NAT'] if 'external_NAT' in n else False
            nic = {
                "network": f"{build_id}-{n['network']}",
                "internal_IP": n['internal_IP'],
                "subnet": f"{build_id}-{n['network']}-{n['subnet']}",
                "external_NAT": n['external_NAT']
            }
            # Nested VMs are sometimes used for vulnerable servers. This adds those specified IP addresses as
            # aliases to the NIC
            if 'IP_aliases' in n and n['IP_aliases']:
                alias_ip_ranges = []
                for ipaddr in n['IP_aliases']:
                    alias_ip_ranges.append({"ipCidrRange": ipaddr})
                nic['aliasIpRanges'] = alias_ip_ranges
            self.networks.append(nic)

            if n.get('dns', False):
                self.dns = f"{self.server_name}"
        # Competitions may have meta_data defined, but compute workouts use assessments. First, check for meta_data
        # if this is a competition, and then look for startup scripts which have been identified from the assessment
        self.meta_data = server_spec.get("meta_data", None)
        if not self.meta_data and startup_scripts and base_name in startup_scripts:
            self.meta_data = startup_scripts[base_name]
        self.student_entry = student_entry
        self.guacamole_startup_script = server_spec.get('guacamole_startup_script', None)
        self.options = options
        
    def commit_to_cloud(self):
        config = {'name': self.server_name}
        if self.machine_type:
            config['machineType'] = f"zones/{zone}/machineTypes/{self.machine_type}"
        if self.tags:
            config['tags'] = self.tags
        if self.build_type != ComputeBuildTypes.MACHINE_IMAGE:
            image_response = compute.images().get(project=project, image=self.custom_image).execute()
            source_disk_image = image_response['selfLink']
            config['disks'] = [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ]

        if self.networks:
            network_interfaces = []
            for network in self.networks:
                if network.get("external_NAT", None):
                    accessConfigs = {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                else:
                    accessConfigs = None
                add_network_interface = {
                    'network': f'projects/{project}/global/networks/{network["network"]}',
                    'subnetwork': f'regions/us-central1/subnetworks/{network["subnet"]}',
                    'accessConfigs': [
                        accessConfigs
                    ]
                }
                if 'internal_IP' in network:
                    add_network_interface['networkIP'] = network["internal_IP"]

                if 'aliasIpRanges' in network:
                    add_network_interface['aliasIpRanges'] = network['aliasIpRanges']
                network_interfaces.append(add_network_interface)
            config['networkInterfaces'] = network_interfaces
        # Allow the instance to access cloud storage and logging.
        config['serviceAccounts'] = [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]

        if self.meta_data:
            config['metadata'] = {'items': [self.meta_data]}
        if self.sshkey:
            if 'metadata' in config and config['metadata'] and 'items' in config['metadata']:
                config['metadata']['items'].append({"key": "ssh-keys", "value": self.sshkey})
            else:
                config['metadata'] = {'items': [{"key": "ssh-keys", "value": self.sshkey}]}
        if self.network_routing:
            config["canIpForward"] = True
        if self.add_disk:
            new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
                        "source": "projects/" + project + "/zones/" + zone + "/disks/" + self.server_name + "-disk"}
            config['disks'].append(new_disk)
        if self.min_cpu_platform:
            config['minCpuPlatform'] = self.min_cpu_platform
        if self.nested_vm:
            config['advancedMachineFeatures'] = {'enableNestedVirtualization': self.nested_vm}

        new_server = datastore.Entity(key=ds_client.key('cybergym-server', self.server_name),
                                      exclude_from_indexes=['guacamole_startup_script'])

        new_server.update({
            'name': self.server_name,
            'workout': self.build_id,
            'build_type': self.build_type,
            'machine_image': self.machine_image,
            'config': config,
            'add_disk': self.add_disk,
            'state': BUILD_STATES.READY,
            'state-timestamp': str(calendar.timegm(time.gmtime())),
            'student_entry': self.student_entry,
            'guacamole_startup_script': self.guacamole_startup_script,
            'snapshot': self.snapshot,
            'dns': self.dns
        })

        if self.options:
            self._process_server_options(new_server, self.options)

        try:
            ds_client.put(new_server)
        except:
            cloud_log(LogIDs.MAIN_APP, f"Error storing server config for {self.server_name}", LOG_LEVELS.ERROR)
            raise

    @staticmethod
    def _process_server_options(server, options):
        """
        Process a list of options which may be included with the server.
        @param server: The server specification
        @type server: Datastore entry of type cybergym-server
        @param options: A list of available options for managing the build of the server
        @type options: List
        @return: server
        @rtype: Datastore entry
        """
        for option in options:
            if type(option) == str and option == "delayed_start":
                server["delayed_start"] = True
