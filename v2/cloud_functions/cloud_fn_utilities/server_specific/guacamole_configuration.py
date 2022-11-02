from enum import Enum
import time
import string
import random
from netaddr import IPAddress, IPNetwork
from google.cloud import logging_v2
import logging

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class GuacamoleConfiguration:
    def __init__(self, build_id):
        self.build_id = build_id
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.connection_ctr = 1

    def prepare_guac_connection(self, connection, server_ip):
        """
        Prepare the guacamole connections in a class array which can be converted to a Guacamole SQL Script
        @return: connection
        @rtype: Dict
        """
        username = connection.get('username', None)
        domain = connection.get('domain', None)
        security_mode = connection.get('security_mode', 'nla')
        connection = {
            'build_id': self.build_id,
            'protocol': connection.get('protocol', 'rdp'),
            'ip': server_ip,
            'workspace_username': f'cyberarena{self.connection_ctr}',
            'workspace_password': self._get_random_password(),
            'connection_user': username,
            'connection_password': self._make_safe_password(connection['password']),
            'domain': domain,
            'security_mode': security_mode,
            'connection_name': f"{self.build_id}-{self.connection_ctr}"
        }
        self.connection_ctr += 1
        return connection

    def get_guac_startup_script(self, connections):
        startup_script = GuacSQL.guac_startup_begin.format(guacdb_password=self.env.guac_db_password)
        for connection in connections:
            guac_user = connection['workspace_username']
            guac_password = connection['workspace_password']
            connection_name = connection['connection_name']
            startup_script += GuacSQL.guac_startup_user_add.format(user=guac_user,
                                                                   name=guac_user,
                                                                   guac_password=guac_password)
            if connection['protocol'] == 'vnc':
                startup_script += GuacSQL.guac_startup_vnc.format(ip=connection['ip'],
                                                                  connection=connection_name,
                                                                  vnc_password=connection['connection_password'])
            else:
                startup_script += GuacSQL.guac_startup_rdp.format(ip=connection['ip'],
                                                                  connection=connection_name,
                                                                  rdp_username=connection['connection_user'],
                                                                  rdp_password=connection['connection_password'],
                                                                  security_mode=connection['security_mode'])
                if connection['domain']:
                    startup_script += GuacSQL.guac_startup_rdp_domain.format(domain=connection['domain'])
            startup_script += GuacSQL.guac_startup_join_connection_user
        startup_script += GuacSQL.guac_startup_end
        return startup_script

    @staticmethod
    def _get_random_password():
        password_length = 12
        letters_and_digits = string.ascii_letters + string.digits
        password = ''.join((random.choice(letters_and_digits) for i in range(password_length)))
        return GuacamoleConfiguration._make_safe_password(password)

    @staticmethod
    def _make_safe_password(password):
        safe_password = password.replace('$', '\$')
        safe_password = safe_password.replace("'", "\'")
        return safe_password


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