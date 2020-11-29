import time
import random
import string

from common.globals import ds_client, project, compute, region, zone, workout_globals, guac_password, BUILD_STATES
from common.dns_functions import add_dns_record
from common.stop_compute import stop_workout, stop_arena
from common.assessment_functions import get_startup_scripts
from common.networking_functions import create_network, create_route, create_firewall_rules
from common.prepare_compute import create_instance_custom_image, build_guacamole_server
from common.state_transition import state_transition, check_ordered_arenas_state


student_network_name = 'student-network'
student_network_subnet = '10.1.0.0/24'


# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def build_student_network(build_id, subnet):
    student_network = [
        {
            'name': student_network_name,
            'subnets': [{'name': 'default', 'ip_subnet': subnet}]
        }
    ]
    create_network(networks=student_network, build_id=build_id)


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
    # STATE: BUILDING_ARENA_NETWORKS
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_STUDENT_NETWORKS):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_STUDENT_NETWORKS)
        # If all of the student servers are in the same network, then create a single network first
        guac_network = ''
        if network_type == 'same':
            build_student_network(build_id=unit_id, subnet=student_network_subnet)
            network_name = "%s-%s" % (unit_id, student_network_name)
            subnet_name = "%s-%s-%s" % (unit_id, student_network_name, 'default')
            guac_network = network_name
        elif network_type == 'distinct':
            for workout_id in workouts:
                i = 0 if i == 0 else i + 1
                build_student_network(build_id=workout_id, subnet='10.1.' + str(i) + '.0/24')
                network_name = "%s-%s" % (workout_id, student_network_name)
                subnet_name = "%s-%s-%s" % (workout_id, student_network_name, 'default')
                if not guac_network:
                    guac_network = network_name
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_STUDENT_NETWORKS)

    # STATE: BUILDING_ARENA_SERVERS
    # The IP address of each server is dynamically assigned as 10.1.i.j
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_STUDENT_SERVERS):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_STUDENT_SERVERS)
        i = 0
        j = 2
        guacamole_connections = []
        for workout_id in workouts:
            workout_key = ds_client.key('cybergym-workout', workout_id)
            workout = ds_client.get(workout_key)

            for server in workout['student_servers']:
                internal_ip_address = f'10.1.{i}.{j}'
                if server['name'] == student_entry_server:
                    rdp_domain = server['domain'] if 'domain' in server else None
                    security_mode = server['security-mode'] if 'security-mode' in server else 'nla'
                    guac_connection = {
                        'workout_id': workout_id,
                        'entry_type': student_entry_type,
                        'ip': internal_ip_address,
                        'username': student_entry_username,
                        'password': student_entry_password,
                        'domain': rdp_domain,
                        'security-mode': security_mode
                    }
                    guacamole_connections.append(guac_connection)
                server_name = "%s-%s" % (workout_id, server['name'])
                sshkey = server["sshkey"]
                tags = server['tags']
                machine_type = server["machine_type"]
                network_routing = server["network_routing"]
                nics = [{
                    "network": network_name,
                    "internal_IP": internal_ip_address,
                    "subnet": subnet_name,
                    "external_NAT": False
                }]
                # Metadata startup scripts are needed for servers in the arena because, unlike workouts, there
                # is no assessment function associated with Arenas at this time.
                meta_data = None
                if server['include_env']:
                    if server['operating-system'] == 'windows':
                        env_startup = workout_globals.windows_startup_script_env.format(env_workoutid=workout_id)
                    else:
                        env_startup = workout_globals.linux_startup_script_env.format(env_workoutid=workout_id)
                    meta_data = {"key": "startup-script", "value": env_startup}
                create_instance_custom_image(compute=compute, workout=workout_id, name=server_name,
                                             custom_image=server['image'], machine_type=machine_type,
                                             networkRouting=network_routing, networks=nics, tags=tags,
                                             meta_data=meta_data, sshkey=sshkey)
                j += 1
        # Build the workout entry server and create the firewall rule to make it accessible.
        build_guacamole_server(build=unit, network=guac_network,
                               guacamole_connections=guacamole_connections)
        # Get the unit datastore entry again because building the guacamole server adds credentials.
        unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_STUDENT_SERVERS)


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

    if 'state' not in unit or not unit['state']:
        state_transition(entity=unit, new_state=BUILD_STATES.START)

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

    # STATE: BUILDING_ARENA_NETWORKS
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_NETWORKS):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_NETWORKS)
        if arena['networks']:
            print('Creating additional arena networks')
            create_network(networks=arena['networks'], build_id=unit_id)
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_NETWORKS)

    # STATE: BUILDING_ARENA_SERVERS
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_SERVERS):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_SERVERS)
        print('Creating additional servers')
        i = 101
        if 'servers' in arena and arena['servers']:
            for server in arena['servers']:
                server_name = "%s-%s" % (unit_id, server['name'])
                sshkey = server["sshkey"]
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
                                             meta_data=None, sshkey=sshkey)
                i += 1
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_SERVERS)

    # STATE: BUILDING_ROUTES
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ROUTES):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ROUTES)
        print('Creating network routes and firewall rules')
        if 'routes' in arena and arena['routes']:
            for route in arena['routes']:
                r = {"name": "%s-%s" % (unit_id, route['name']),
                     "network": "%s-%s" % (unit_id, route['network']),
                     "destRange": route['dest_range'],
                     "nextHopInstance": "%s-%s" % (unit_id, route['next_hop_instance'])}
                create_route(route)
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ROUTES)

    # STATE: BUILDING_FIREWALL
    if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_FIREWALL):
        state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_FIREWALL)
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

        # Create the default rules to allow traffic between student networks.
        firewall_rules.append({"name": "%s-%s" % (unit_id, 'allow-all-internal'),
                               "network": "%s-%s" % (unit_id, student_network_name),
                               "targetTags": [],
                               "protocol": 'tcp',
                               "ports": ['tcp/any', 'udp/any', 'icmp/any'],
                               "sourceRanges": [student_network_subnet]})

        create_firewall_rules(firewall_rules)
        state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_FIREWALL)

    state_transition(entity=unit, new_state=BUILD_STATES.READY)
