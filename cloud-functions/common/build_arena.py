import time
import random
import string

from common.globals import ds_client, project, compute, region, zone, workout_globals, guac_password
from common.dns_functions import add_dns_record, register_workout_server
from common.stop_compute import stop_workout, stop_arena
from common.assessment_functions import get_startup_scripts
from common.networking_functions import create_network, create_route, create_firewall_rules
from common.compute_functions import create_instance_custom_image, get_server_ext_address


student_network_name = 'student-network'
student_entry_image = 'image-labentry'
student_network_subnet = '10.1.0.0/24'


# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def get_random_alphaNumeric_string(stringLength=12):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))


def build_student_network(build_id, subnet):
    student_network = [
        {
            'name': student_network_name,
            'subnets': [{'name': 'default', 'ip_subnet': subnet}]
        }
    ]
    create_network(networks=student_network, build_id=build_id)


def build_guacamole_server(unit_id, network, guacamole_connections):
    """
    Builds an image with an Apache Guacamole server and adds startup scripts to insert the
    correct users and connections into the guacamole database. This server becomes the entrypoint
    for all students in the arena.
    :param unit_id: Build ID for the unit. This is used for the server name.
    :param network: The network name for the server
    :param guacamole_connections: An array of dictionaries for each student {workoutid, ip address of their server,
        and password for their server.
    :return: Null
    """
    if len(guacamole_connections) == 0:
        return None

    startup_script = workout_globals.guac_startup_begin.format(guacdb_password=guac_password)
    i = 0
    for connection in guacamole_connections:
        # Get a PRNG password for the workout and store it with the datastore record for display on the workout controller
        guac_user = 'cybergym' + str(i+1)
        guac_connection_password = get_random_alphaNumeric_string()
        workout_key = ds_client.key('cybergym-workout', connection['workout_id'])
        workout = ds_client.get(workout_key)
        workout['workout_user'] = guac_user
        workout['workout_password'] = guac_connection_password
        ds_client.put(workout)

        startup_script += workout_globals.guac_startup_user_add.format(user=guac_user,
                                                                       name=guac_user,
                                                                       guac_password=guac_connection_password)
        if connection['entry_type'] == 'vnc':
            startup_script += workout_globals.guac_startup_vnc.format(ip=connection['ip'],
                                                                      connection=connection['workout_id'],
                                                                      vnc_password=connection['password'])
        else:
            startup_script += workout_globals.guac_startup_rdp.format(ip=connection['ip'],
                                                                      connection=connection['workout_id'],
                                                                      rdp_username=connection['username'],
                                                                      rdp_password=connection['password'])
        startup_script += workout_globals.guac_startup_join_connection_user
        i += 1
    startup_script += workout_globals.guac_startup_end

    server_name = "%s-%s" % (unit_id, 'student-guacamole')
    tags = {'items': ['student-entry']}
    nics = [{
        "network": network,
        "internal_IP": '10.1.0.100',
        "subnet": "%s-%s" % (network, 'default'),
        "external_NAT": True
    }]
    meta_data = {'items': [{"key": "startup-script", "value": startup_script}]}
    create_instance_custom_image(compute=compute, workout=unit_id, name=server_name,
                                 custom_image=student_entry_image, machine_type='n1-standard-1',
                                 networkRouting=False, networks=nics, tags=tags,
                                 meta_data=meta_data, sshkey=None, guac_path=None)
    # Add the external_IP address for the workout. This allows easy deletion of the DNS record when deleting the arena
    ip_address = get_server_ext_address(server_name)
    add_dns_record(unit_id, ip_address)
    key = ds_client.key('cybergym-unit', unit_id)
    build = ds_client.get(key)
    build["external_ip"] = ip_address
    ds_client.put(build)
    # Create the firewall rule allowing access to the guacamole connection
    allow_entry = [
        {
            "name": "%s-%s" % (unit_id, 'allow-student-entry'),
            "network": network,
            "targetTags": ['student-entry'],
            'protocol': None,
            'ports': ['tcp/80,8080,443'],
            'sourceRanges': ['0.0.0.0/0']
        }
    ]
    create_firewall_rules(allow_entry)


def build_student_servers(unit_id, workouts, student_entry_server, student_entry_type, student_entry_username,
                          student_entry_password, network_type):
    """
    Builds the student servers for the arena. In the arena, all student servers have the same configuration.
    However, they may be on distinct networks or the same network.
    :param unit_id: Unit ID for the Arena build. This is used to pull data from the datastore
    :param workouts: An array of workout_ids for this arena.
    :param student_entry_server: The name of the server used for students to access the arena
    :param student_entry_type: Either vnc or rdp
    :param student_entry_username: The username for the server or None for vnc
    :param student_entry_password: The password for the server
    :param network_type: Either a same network for all students or each student gets their distinct workout.
    :return:
    """
    # If all of the student servers are in the same network, then create a single network first
    guac_network = ''
    if network_type == 'same':
        build_student_network(build_id=unit_id, subnet=student_network_subnet)
        network_name = "%s-%s" % (unit_id, student_network_name)
        subnet_name = "%s-%s-%s" % (unit_id, student_network_name, 'default')
        guac_network = network_name

    # The IP address of each server is dynamically assigned as 10.1.i.j
    i = 0
    j = 2
    guacamole_connections = []
    for workout_id in workouts:
        workout_key = ds_client.key('cybergym-workout', workout_id)
        workout = ds_client.get(workout_key)

        if network_type == 'distinct':
            i = 0 if i == 0 else i + 1
            build_student_network(build_id=workout_id, subnet='10.1.' + str(i) + '.0/24')
            network_name = "%s-%s" % (workout_id, student_network_name)
            subnet_name = "%s-%s-%s" % (workout_id, student_network_name, 'default')
            if not guac_network:
                guac_network = network_name
            i += 1
            j = 2
        for server in workout['student_servers']:
            internal_ip_address = f'10.1.{i}.{j}'
            if server['name'] == student_entry_server:
                guac_connection = {
                    'workout_id': workout_id,
                    'entry_type': student_entry_type,
                    'ip': internal_ip_address,
                    'username': student_entry_username,
                    'password': student_entry_password
                }
                guacamole_connections.append(guac_connection)
            server_name = "%s-%s" % (workout_id, server['name'])
            sshkey = server["sshkey"]
            guac_path = server['guac_path']
            tags = server['tags']
            machine_type = server["machine_type"]
            network_routing = server["network_routing"]
            nics = [{
                "network": network_name,
                "internal_IP": internal_ip_address,
                "subnet": subnet_name,
                "external_NAT": False
            }]
            create_instance_custom_image(compute=compute, workout=workout_id, name=server_name,
                                         custom_image=server['image'], machine_type=machine_type,
                                         networkRouting=network_routing, networks=nics, tags=tags,
                                         meta_data=None, sshkey=sshkey, guac_path=None)
            j += 1
    # Build the workout entry server and create the firewall rule to make it accessible.
    build_guacamole_server(unit_id=unit_id, network=guac_network, guacamole_connections=guacamole_connections)


def build_arena(unit_id):
    """
    Builds an arena of student servers and a common compute environment according to the specification referenced in
    the workout_unit datastore
    :param unit_id: The workout_id key in the datastore holding the build specification
    :return: None
    """
    key = ds_client.key('cybergym-unit', unit_id)
    unit = ds_client.get(key)
    # This can sometimes happen when debugging a Unit ID and the Datastore record no longer exists.
    arena = unit['arena']
    if not arena:
        print('No unit %s exists in the data store' % unit_id)
        return

    # # Parse the assessment specification to obtain any startup scripts for the workout.
    # startup_scripts = None
    # if unit['assessment']:
    #     startup_scripts = get_startup_scripts(workout_id=workout_id, assessment=workout['assessment'])
    # # Create the networks and subnets
    # First create the student servers
    print('Creating student servers')
    build_student_servers(unit_id=unit_id, workouts=unit['workouts'],
                          student_entry_type=arena['student_entry_type'],
                          student_entry_server=arena['student_entry'],
                          student_entry_username=arena['student_entry_username'],
                          student_entry_password=arena['student_entry_password'],
                          network_type=arena['student_network_type'])

    if arena['networks']:
        print('Creating additional arena networks')
        create_network(networks=arena['networks'], build_id=unit_id)

    # Now create the arena servers
    print('Creating additional servers')
    i = 101
    for server in arena['servers']:
        server_name = "%s-%s" % (unit_id, server['name'])
        sshkey = server["sshkey"]
        guac_path = server['guac_path']
        tags = server['tags']
        machine_type = server["machine_type"]
        network_routing = server["network_routing"]
        # If a nic is not specified, then add the server to the student-network.
        if server['nics']:
            nics = []
            for n in server['nics']:
                if 'network' not in n:
                    n['network'] = student_network_name
                if 'internal_IP' not in n:
                    n['internal_IP'] = f'10.1.0.{i}'
                if 'subnet' not in n:
                    n['subnet'] = 'default'
                if 'external_NAT' not in n:
                    n['external_NAT'] = False
                nic = {
                    "network": "%s-%s" % (unit_id, n['network']),
                    "internal_IP": n['internal_IP'],
                    "subnet": "%s-%s-%s" % (unit_id, n['network'], n['subnet']),
                    "external_NAT": n['external_NAT']
                }
                nics.append(nic)
        else:
            nics = [
                {
                    "network": "%s-%s" % (unit_id, student_network_name),
                    "internal_IP": f'10.1.0.{i}',
                    "subnet": "%s-%s-%s" % (unit_id, student_network_name, 'default'),
                    "external_NAT": False
                }
            ]

        create_instance_custom_image(compute=compute, workout=unit_id, name=server_name,
                                     custom_image=server['image'], machine_type=machine_type,
                                     networkRouting=network_routing, networks=nics, tags=tags,
                                     meta_data=None, sshkey=sshkey, guac_path=guac_path)
        i += 1

    # Create all of the network routes and firewall rules
    print('Creating network routes and firewall rules')
    if 'routes' in arena and arena['routes']:
        for route in arena['routes']:
            r = {"name": "%s-%s" % (unit_id, route['name']),
                 "network": "%s-%s" % (unit_id, route['network']),
                 "destRange": route['dest_range'],
                 "nextHopInstance": "%s-%s" % (unit_id, route['next_hop_instance'])}
            create_route(route)

    firewall_rules = []
    for rule in arena['firewall_rules']:
        if 'network' not in rule:
            rule['network'] = student_network_name
        firewall_rules.append({"name": "%s-%s" % (unit_id, rule['name']),
                               "network": "%s-%s" % (unit_id, rule['network']),
                               "targetTags": rule['target_tags'],
                               "protocol": rule['protocol'],
                               "ports": rule['ports'],
                               "sourceRanges": rule['source_ranges']})

    create_firewall_rules(firewall_rules)

    stop_arena(unit_id)

    unit['complete'] = True
    ds_client.put(unit)
