"""
The competition (a.k.a. Arena) server specification is unique because each student has a set of servers, and the
Arena (or unit) also has a set of servers. The logic to parse through the specification and create new server
specifications is included here.
"""

from utilities.globals import workout_globals, LOG_LEVELS, cloud_log, BuildTypes
from utilities.infrastructure_as_code.server_spec_to_cloud import ServerSpecToCloud
from utilities.infrastructure_as_code.student_entry_spec_to_cloud import StudentEntrySpecToCloud


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"

class CompetitionServerSpecToCloud:
    STUDENT_NETWORK_NAME = 'student-network'
    STUDENT_NETWORK_SUBNET = '10.1.0.0/16'
    STUDENT_DEFAULT_GUAC_IP = "10.1.0.2"

    def __init__(self, unit, workout_ids, workout_specs):
        self.unit_id = unit.key.name
        self.unit = unit
        self.workout_specs = workout_specs
        self.workout_ids = workout_ids
        self.arena = self.unit.get('arena', None)
        if not self.arena:
            cloud_log(self.unit_id, f"Build operation failed. No unit {self.unit_id} exists in the data store",
                      LOG_LEVELS.ERROR)
            raise LookupError
        self.student_entry_type = self.arena['student_entry_type']
        self.student_entry_server = self.arena['student_entry']
        self.student_entry_username = self.arena['student_entry_username']
        self.student_entry_password = self.arena['student_entry_password']
        self.network_type = self.arena['student_network_type']

    def commit_to_cloud(self):
        """
        The competition arena first commits all servers for each student, and then it creates the student
        entry guacamole server. Finally, any arena servers are committed.
        @return:
        @rtype:
        """
        j = 3
        for i, workout_spec in enumerate(self.workout_specs):
            workout_id = self.workout_ids[i]
            for server in workout_spec['student_servers']:
                internal_ip_address = f'10.1.{i}.{j}'
                external_nat = server.get('external_nat', False)
                server['nics'] = [{
                    "network": self.STUDENT_NETWORK_NAME,
                    "internal_IP": internal_ip_address,
                    "subnet": "default",
                    "external_NAT": external_nat
                }]
                # Metadata startup scripts are needed for servers in the arena because, unlike workouts, there
                # is no assessment function associated with Arenas at this time.
                meta_data = None
                if server.get('include_env', None):
                    if server.get('operating-system', None) == 'windows':
                        env_startup = workout_globals.windows_startup_script_env.format(env_workoutid=workout_id)
                        meta_data = {"key": "windows-startup-script-cmd", "value": env_startup}
                    else:
                        env_startup = workout_globals.linux_startup_script_env.format(env_workoutid=workout_id)
                        meta_data = {"key": "startup-script", "value": env_startup}
                server['meta_data'] = meta_data
                ServerSpecToCloud(server_spec=server, build_id=self.unit_id).commit_to_cloud()
                j += 1
        self._commit_student_entry()
        self._commit_shared_servers()

    def _commit_student_entry(self):
        """
        Loop through each workout to create the student entry configuration for the competition arena
        @return: None
        @rtype: None
        """
        guacamole_connections = []
        for i, workout_spec in enumerate(self.workout_specs):
            workout_id = self.workout_ids[i]
            for server in workout_spec['student_servers']:
                if server['name'] == self.student_entry_server:
                    rdp_domain = server['domain'] if 'domain' in server else None
                    security_mode = server['security-mode'] if 'security-mode' in server else 'nla'
                    internal_ip_address = server['nics'][0]['internal_IP']
                    guac_connection = {
                        'workout_id': workout_id,
                        'type': self.student_entry_type,
                        'ip': internal_ip_address,
                        'username': self.student_entry_username,
                        'password': self.student_entry_password,
                        'domain': rdp_domain,
                        'security-mode': security_mode
                    }
                    guacamole_connections.append(guac_connection)
        StudentEntrySpecToCloud(type=BuildTypes.ARENA, build=self.unit, build_id=self.unit_id,
                                competition_guacamole_connections=guacamole_connections,
                                student_entry_network=self.STUDENT_NETWORK_NAME,
                                student_entry_ip_address=self.STUDENT_DEFAULT_GUAC_IP).commit_to_cloud()

    def _commit_shared_servers(self):
        """
        Competition arenas may have shared servers available for all students. This function submits the
        build specification for these servers. The primary modification needed here is the IP address and
        network configuration for each server.
        @return: None
        """
        if 'servers' in self.arena and self.arena['servers']:
            i = 201
            for server in self.arena['servers']:
                # If a nic is not specified, then add the server to the student-network.
                if server.get('nics', None):
                    nics = []
                    for n in server['nics']:
                        if 'network' not in n:
                            n['network'] = self.STUDENT_NETWORK_NAME
                        if 'internal_IP' not in n:
                            n['internal_IP'] = f'10.1.0.{i}'
                        if 'subnet' not in n:
                            n['subnet'] = 'default'
                        if 'external_NAT' not in n:
                            n['external_NAT'] = False
                        nics.append(n)
                else:
                    nics = [
                        {
                            "network": self.STUDENT_NETWORK_NAME,
                            "internal_IP": f'10.1.0.{i}',
                            "subnet": 'default',
                            "external_NAT": False
                        }
                    ]
                server['nics'] = nics
                ServerSpecToCloud(server_spec=server, build_id=self.unit_id).commit_to_cloud()
