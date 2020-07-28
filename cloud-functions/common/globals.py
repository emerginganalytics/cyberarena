import sys
import random
import string
import googleapiclient.discovery
from google.cloud import datastore, storage

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
dns_suffix = ".cybergym-eac-ualr.org"
project = 'ualr-cybersecurity'
dnszone = 'cybergym-public'
workout_token = 'RG987S1GVNKYRYHYA'
region = 'us-central1'
zone = 'us-central1-a'
script_repository = 'gs://ualr-cybersecurity_cloudbuild/startup-scripts/'
guac_password = 'promiseme'
student_entry_image = 'image-labentry'

# Use this for debugging. Uncomment the above endpoint for final environment.
post_endpoint = 'http://localhost:8080/complete'


class workout_globals():
    MAX_RUN_HOURS = 10
    yaml_bucket = project + '_cloudbuild'
    yaml_folder = 'yaml-build-files/'
    windows_startup_script_env = 'setx /m WORKOUTID {env_workoutid}\n'
    windows_startup_script_task = 'setx /m WORKOUTKEY{q_number} {env_workoutkey}\n' \
                                  'call gsutil cp ' + script_repository + '{script} .\n' \
                                  'schtasks /Create /SC MINUTE /TN {script_name} /RU System /TR {script_command}'
    linux_startup_script_env = '#! /bin/bash\nexport WORKOUTID={env_workoutid}\n'
    linux_startup_script_task = 'export WORKOUTKEY{q_number}={env_workoutkey}\n' \
                                  'gsutil cp ' + script_repository + '{script} /usr/bin\n' \
                                  '(crontab -l 2>/dev/null; echo "* * * * * /usr/bin/{script}") | crontab -'

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
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'password\', \"{vnc_password\");\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'port\', \'5901\');\n'
    guac_startup_rdp = \
        'INSERT INTO guacamole_connection (connection_name, protocol) VALUES (\'{connection}\', \'rdp\');\n' \
        'SELECT connection_id INTO @connection_id FROM guacamole_connection WHERE connection_name = \'{connection}\';\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'hostname\', \'{ip}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'password\', \"{rdp_password}\");\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'port\', \'3389\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'username\', \'{rdp_username}\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'security\', \'nla\');\n' \
        'INSERT INTO guacamole_connection_parameter VALUES (@connection_id, \'ignore-cert\', \'true\');\n'
    guac_startup_join_connection_user = \
        'INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission) VALUES (@entity_id, @connection_id, \'READ\');\n'
    guac_startup_end = 'MY_QUERY\n'

    @staticmethod
    def extended_wait(project, zone, operation_id):
        max_wait = 3
        i = 0
        complete = False
        while not complete and i <= max_wait:
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=operation_id).execute()
                complete = True
            except:
                i += 1

        if not complete:
            print("Timeout for operation %s" % operation_id)
            return False
        else:
            return True

    @staticmethod
    def refresh_api():
        compute = googleapiclient.discovery.build('compute', 'v1')
        return compute


class SERVER_STATES:
    READY = 'READY'
    BUILDING = 'BUILDING'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    STOPPED = 'STOPPED'
    EXPIRED = 'EXPIRED'
    MISFIT = 'MISFIT'
    RESETTING = 'RESETTING'
    RELOADING = 'RELOADING'
    BROKEN = 'BROKEN'


class WORKOUT_STATES:
    START = 'START'
    BUILDING_ASSESSMENT = 'BUILDING_ASSESSMENT'
    BUILDING_NETWORKS = 'BUILDING_NETWORKS'
    COMPLETED_NETWORKS = 'COMPLETED_NETWORKS'
    BUILDING_SERVERS = 'BUILDING_SERVERS'
    COMPLETED_SERVERS = 'COMPLETED_SERVERS'
    BUILDING_ROUTES = 'BUILDING_ROUTES'
    COMPLETED_ROUTES = 'COMPLETED_ROUTES'
    BUILDING_FIREWALL = 'BUILDING_FIREWALL'
    COMPLETED_FIREWALL = 'COMPLETED_FIREWALL'
    BUILDING_STUDENT_ENTRY = 'BUILDING_STUDENT_ENTRY'
    COMPLETED_STUDENT_ENTRY = 'COMPLETED_STUDENT_ENTRY'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    READY = 'READY'
    EXPIRED = 'EXPIRED'
    MISFIT = 'MISFIT'
    BROKEN = 'BROKEN'

ordered_workout_states = {
    WORKOUT_STATES.START: 0,
    WORKOUT_STATES.BUILDING_ASSESSMENT: 1,
    WORKOUT_STATES.BUILDING_NETWORKS: 2,
    WORKOUT_STATES.COMPLETED_NETWORKS: 3,
    WORKOUT_STATES.BUILDING_SERVERS: 4,
    WORKOUT_STATES.COMPLETED_SERVERS: 5,
    WORKOUT_STATES.BUILDING_STUDENT_ENTRY: 6,
    WORKOUT_STATES.COMPLETED_STUDENT_ENTRY: 7,
    WORKOUT_STATES.BUILDING_ROUTES: 8,
    WORKOUT_STATES.COMPLETED_ROUTES: 9,
    WORKOUT_STATES.BUILDING_FIREWALL: 10,
    WORKOUT_STATES.COMPLETED_FIREWALL: 11
}


class PUBSUB_TOPICS:
    MANAGE_SERVER = 'manage-server'


class SERVER_ACTIONS:
    BUILD = 'BUILD'
    START = 'START'
    DELETE = 'DELETE'


def get_random_alphaNumeric_string(stringLength=12):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
