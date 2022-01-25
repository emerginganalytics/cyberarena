"""
Prepares a build spec for an image with an Apache Guacamole server and adds startup scripts to insert the correct
users and connections into the guacamole database. This server becomes the entrypoint for all students in the arena.
"""

import random
import string
from netaddr import IPAddress, IPNetwork
from utilities.globals import ds_client, LOG_LEVELS, cloud_log, LogIDs, \
    BuildTypes, guac_db_password
from utilities.infrastructure_as_code.server_spec_to_cloud import ServerSpecToCloud


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class StudentEntrySpecToCloud:
    STUDENT_ENTRY_IMAGE = 'image-labentry'

    def __init__(self, type, build, build_id, competition_guacamole_connections=None, student_entry_network=None,
                 student_entry_ip_address=None):
        """
        @param type: The build type, COMPUTE or ARENA
        @type type: str
        @param build: A datstore entry of the build specification
        @type build: dict
        @param build_id: The key used for storing the build specification
        @type build_id: str
        @param competition_guacamole_connections: The guacamole connection for competition arenas.
        @type competition_guacamole_connections: list
        @param student_entry_network: The name of the network to place the student entry server (for ARENA build only)
        @type student_entry_network: str
        @param student_entry_ip_address: The IP address of the guac server, default of None
        @type student_entry_ip_address: str
        """
        self.type = type
        self.build = build
        self.build_id = build_id
        self.competition_guacamole_connections = competition_guacamole_connections
        self.student_entry_ip_address = student_entry_ip_address
        # The student entry network is only specified for the arena build. Otherwise, we pull from the build spec
        self.student_entry_network = student_entry_network if student_entry_network \
            else self.build['student_entry']['network']
        self.guac_connections = []
        self.student_credentials = []

    def commit_to_cloud(self):
        """
        Store the student entry server specification for the given workout.
        @return: None
        @rtype:
        """
        self._prepare_guac_connections()

        guac_startup_script = self._get_guac_startup_script(self.guac_connections)
        student_entry_ip = self._get_student_entry_ip_address(self.build, self.student_entry_network) \
            if not self.student_entry_ip_address else self.student_entry_ip_address

        if not student_entry_ip:
            cloud_log(LogIDs.MAIN_APP, "Could not find available IP address for student entry guacamole server",
                      LOG_LEVELS.ERROR)
            raise LookupError

        server_spec = {
            'name': "student-guacamole",
            'image': self.STUDENT_ENTRY_IMAGE,
            'tags': {'items': ['student-entry']},
            'machine_type': 'n1-standard-1',
            'nics': [
                {
                    "network": self.student_entry_network,
                    "subnet": "default",
                    "external_NAT": True,
                    "internal_IP": student_entry_ip
                }
            ],
            'guacamole_startup_script': guac_startup_script
        }
        self._update_build_spec()
        ServerSpecToCloud(server_spec, self.build_id, student_entry=True).commit_to_cloud()

    def _prepare_guac_connections(self):
        """
        Prepare the guacamole connections and the student credentials. This considers the following build types:
        1) Compute Workout with only 1 credential - This is an older structure that predated the need for multiple
            credentials.
        2) Compute Workout with multiple credential - In this case, the specification has a 'connections' element
        3) Competition arenas - These have 1 user per student in the competition and have multiple workout IDs
        @return: None
        @rtype: None
        """
        raw_connections = None
        if self.type == BuildTypes.ARENA:
            raw_connections = self.competition_guacamole_connections
        else:
            if 'connections' in self.build['student_entry']:
                raw_connections = self.build['student_entry']['connections']
            else:
                connection = self._create_guac_connection(self.build_id, self.build['student_entry'], 0)
                self.student_credentials.append({
                    "workout_user": connection['student_user'],
                    "workout_password": connection['student_password']
                })
                self.guac_connections.append(connection)

        # This occurs for 1) competition builds and 2) compute builds with more than one connection
        if raw_connections:
            i = 0
            for entry in raw_connections:
                connection = self._create_guac_connection(self.build_id, entry, i)
                self.student_credentials.append({
                    "workout_id": entry.get('workout_id', None),
                    "workout_user": connection['student_user'],
                    "workout_password": connection['student_password']
                })
                self.guac_connections.append(connection)
                i += 1

    def _create_guac_connection(self, build_id, config, connection_number):
        """
        Creates a guacamole connection ready for inserting into the student entry server configuration.
        @param build_id: ID of the workout being created
        @type build_id: string
        @param config: Specification string for a student guacamole connection
        @type config: dict
        @param connection_number: The iterator number for the connection
        @type connection_number: int
        @return: The specification with the workout ID and student credentials added
        @rtype: dict
        """
        student_entry_username = config['username'] if 'username' in config else None
        rdp_domain = config['domain'] if 'domain' in config else None
        security_mode = config['security-mode'] if 'security-mode' in config else 'nla'
        connection = {
            'build_id': build_id,
            'entry_type': config['type'],
            'ip': config['ip'],
            "student_user": f'cybergym{connection_number + 1}',
            "student_password": self._get_random_alphaNumeric_string(),
            "connection_name": f"{build_id}-{connection_number}",
            'connection_user': student_entry_username,
            'connection_password': self._get_safe_password(config['password']),
            'domain': rdp_domain,
            'security-mode': security_mode
        }
        return connection

    def _update_build_spec(self):
        """
        Add credentials for the student entry to the workout, and add a default firewall rule to allow access
        to the student entry server.
        When the build type is an arena, each workout in the arena needs to have added the recently generated
        credentials.
        @param credentials: Credentials for users in a given build
        @type credentials: list of dict
        @param network_name: The name of the network the student entry server resides in
        @type: str
        @return: Status
        @rtype: bool
        """
        # Build the firewall rule to allow external access to the student entry.
        firewall_rule = {
            'name': 'allow-student-entry',
            'network': self.student_entry_network,
            'target_tags': ['student-entry'],
            'protocol': None,
            'ports': ['tcp/80,8080,443'],
            'source_ranges': ['0.0.0.0/0']
        }
        if self.type == BuildTypes.COMPUTE:
            if len(self.student_credentials) > 1:
                self.build['workout_credentials'] = self.student_credentials
            else:
                self.build['workout_user'] = self.student_credentials[0]['workout_user']
                self.build['workout_password'] = self.student_credentials[0]['workout_password']
            self.build['firewall_rules'].append(firewall_rule)
        elif self.type == BuildTypes.ARENA:
            for credential in self.student_credentials:
                workout_id = credential['workout_id']
                student_user = credential['workout_user']
                student_password = credential['workout_password']
                workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
                workout['workout_user'] = student_user
                workout['workout_password'] = student_password
                ds_client.put(workout)
            self.build['arena']['firewall_rules'].append(firewall_rule)
        ds_client.put(self.build)
        return True

    @staticmethod
    def _get_random_alphaNumeric_string(stringLength=12):
        lettersAndDigits = string.ascii_letters + string.digits
        password = StudentEntrySpecToCloud\
            ._get_safe_password(''.join((random.choice(lettersAndDigits) for i in range(stringLength))))
        return password

    @staticmethod
    def _get_safe_password(password):
        safe_password = password.replace('$', '\$')
        safe_password = safe_password.replace("'", "\'")
        return safe_password

    @staticmethod
    def _get_guac_startup_script(guac_connections):
        startup_script = GuacSQL.guac_startup_begin.format(guacdb_password=guac_db_password)
        for connection in guac_connections:
            guac_user = connection['student_user']
            guac_password = connection['student_password']
            connection_name = connection['connection_name']
            startup_script += GuacSQL.guac_startup_user_add.format(user=guac_user,
                                                                           name=guac_user,
                                                                           guac_password=guac_password)
            if connection['entry_type'] == 'vnc':
                startup_script += GuacSQL.guac_startup_vnc.format(ip=connection['ip'],
                                                                          connection=connection_name,
                                                                          vnc_password=connection['connection_password'])
            else:
                startup_script += GuacSQL.guac_startup_rdp.format(ip=connection['ip'],
                                                                          connection=connection_name,
                                                                          rdp_username=connection['connection_user'],
                                                                          rdp_password=connection['connection_password'],
                                                                          security_mode=connection['security-mode'])
                if connection['domain']:
                    startup_script += GuacSQL.guac_startup_rdp_domain.format(domain=connection['domain'])
            startup_script += GuacSQL.guac_startup_join_connection_user
        startup_script += GuacSQL.guac_startup_end
        return startup_script

    @staticmethod
    def _get_student_entry_ip_address(build, network):
        """
        Find the first available IP address to use for the student entry server.
        @param workout: Datastore entry for the workout
        @param network: The network name for the workout
        @return: An available IP address
        @rtype: str
        """
        build_id = build.key.name
        network = network.replace(f"{build_id}-", '')
        ip_subnet = None
        for network_name in build['networks']:
            if network_name['name'] == network:
                ip_subnet = IPNetwork(network_name['subnets'][0]['ip_subnet'])

        unavailable = []
        for server in build['servers']:
            for n in server['nics']:
                if n['network'] == network:
                    unavailable.append(IPAddress(n['internal_IP']))

        if not ip_subnet:
            return False
        i = 0
        for ip_address in ip_subnet:
            if i > 1 and ip_address not in unavailable:
                return str(ip_address)
            i += 1
        return False


class GuacSQL:
    # These next few constants build the startup scripts for guacamole. This is VERY helpful!
    # The elusive Apache Guacamole documentation for the SQL commands are here: https://guacamole.apache.org/doc/gug/jdbc-auth.html
    guac_startup_begin = \
        '#!/bin/bash\n' \
        'mysql -u guacamole_user -p{guacdb_password} -D guacamole_db <<MY_QUERY\n'
    guac_startup_user_add = \
        'SET @salt = UNHEX(SHA2(UUID(), 256));\n' \
        'INSERT INTO guacamole_entity (name, type) VALUES (\'{user}\', \'USER\');\n' \
        'SELECT entity_id INTO @entity_id FROM guacamole_entity WHERE name = \'{user}\';\n' \
        'INSERT INTO guacamole_user (entity_id, password_salt, password_hash, password_date) ' \
        'VALUES (@entity_id, @salt, UNHEX(SHA2(CONCAT(\'{guac_password}\', HEX(@salt)), 256)), \'2020-06-12 00:00:00\');\n'
    guac_startup_vnc = \
        'INSERT INTO guacamole_connection (connection_name, protocol) VALUES (\'{connection}\', \'vnc\');\n' \
        'SELECT connection_id INTO @connection_id FROM guacamole_connection WHERE connection_name = \'{connection}\';\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'hostname\', \'{ip}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'password\', \"{vnc_password}\");\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'port\', \'5901\');\n'
    guac_startup_rdp = \
        'INSERT INTO guacamole_connection (connection_name, protocol) VALUES (\'{connection}\', \'rdp\');\n' \
        'SELECT connection_id INTO @connection_id FROM guacamole_connection WHERE connection_name = \'{connection}\';\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'hostname\', \'{ip}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'password\', \"{rdp_password}\");\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'port\', \'3389\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'username\', \'{rdp_username}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'security\', \'{security_mode}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'ignore-cert\', \'true\');\n'
    guac_startup_rdp_domain = \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'domain\', \'{domain}\');\n'
    guac_startup_join_connection_user = \
        'INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission) VALUES (@entity_id, @connection_id, \'READ\');\n'
    guac_startup_end = 'MY_QUERY\n'
