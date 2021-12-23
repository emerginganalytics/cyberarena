import random
import string
import time
from common.globals import ds_client, log_client, project, compute, region, zone, BUILD_STATES, LOG_LEVELS
from common.assessment_functions import get_startup_scripts
from common.networking_functions import create_route, create_firewall_rules, workout_route_setup
from common.prepare_compute import create_instance_custom_image, build_guacamole_server
from common.state_transition import state_transition, check_ordered_workout_state
from googleapiclient.errors import HttpError


# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def create_guac_connection(workout_id, config):
    """
    Creates a guacamole connection ready for inserting into the student entry server configuration.
    @param workout_id: ID of the workout being created
    @type workout_id: string
    @param config: Specification string for a student guacamole connection
    @type config: dict
    @return: The specification with the workout ID included
    @rtype: dict
    """
    student_entry_username = config['username'] if 'username' in config else None
    rdp_domain = config['domain'] if 'domain' in config else None
    security_mode = config['security-mode'] if 'security-mode' in config else 'nla'
    connection = {
        'workout_id': workout_id,
        'entry_type': config['type'],
        'ip': config['ip'],
        'username': student_entry_username,
        'password': config['password'],
        'domain': rdp_domain,
        'security-mode': security_mode
    }
    return connection


def build_workout(workout_id):
    """
    Builds a workout compute environment according to the specification referenced in the datastore with key workout_id
    :param workout_id: The workout_id key in the datastore holding the build specification
    :return: None
    """
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    # This can sometimes happen when debugging a workout ID and the Datastore record no longer exists.
    if not workout:
        g_logger = log_client.logger('cybergym-app-error')
        g_logger.log_struct(
            {
                "message": "Build operation failed. No workout for {} exists in the data store".format(workout_id)
            }, severity=LOG_LEVELS.WARNING
        )
        return
    g_logger = log_client.logger(str(workout_id))
    startup_scripts = None
    # Parse the assessment specification to obtain any startup scripts for the workout.
    if 'state' not in workout or not workout['state']:
        state_transition(entity=workout, new_state=BUILD_STATES.START)

    if workout['assessment']:
        startup_scripts = get_startup_scripts(workout_id=workout_id, assessment=workout['assessment'])
    # Create the networks and subnets
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_NETWORKS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_NETWORKS)
        g_logger.log_struct(
            {
                "message": "Building networks",
            }, severity=LOG_LEVELS.INFO
        )
        for network in workout['networks']:
            network_body = {"name": "%s-%s" % (workout_id, network['name']),
                            "autoCreateSubnetworks": False,
                            "region": region}
            try:
                response = compute.networks().insert(project=project, body=network_body).execute()
                compute.globalOperations().wait(project=project, operation=response["id"]).execute()
                time.sleep(10)
            except HttpError as err:
                # If the network already exists, then this may be a rebuild and ignore the error
                if err.resp.status in [409]:
                    pass
            for subnet in network['subnets']:
                subnetwork_body = {
                    "name": "%s-%s" % (network_body['name'], subnet['name']),
                    "network": "projects/%s/global/networks/%s" % (project, network_body['name']),
                    "ipCidrRange": subnet['ip_subnet']
                }
                try:
                    response = compute.subnetworks().insert(project=project, region=region,
                                                            body=subnetwork_body).execute()
                    compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()
                except HttpError as err:
                    # If the subnetwork already exists, then this may be a rebuild and ignore the error
                    if err.resp.status in [409]:
                        pass
            state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_NETWORKS)

    # Now create the server configurations
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_SERVERS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_SERVERS)
        g_logger.log_struct(
            {
                "message": "Building servers"
            }, severity=LOG_LEVELS.INFO
        )
        for server in workout['servers']:
            custom_image = server.get('image', None)
            build_type = server.get("build_type", None)
            machine_image = server.get("machine_image", None)
            server_name = "%s-%s" % (workout_id, server['name'])
            sshkey = server.get("sshkey", None)
            tags = server.get('tags', None)
            machine_type = server.get("machine_type", None)
            network_routing = server.get("network_routing", None)
            min_cpu_platform = server.get("minCpuPlatform", None)
            add_disk = server.get("add_disk", None)
            options = server.get("options", None)
            snapshot = server.get('snapshot', None)
            nics = []
            for n in server['nics']:
                n['external_NAT'] = n['external_NAT'] if 'external_NAT' in n else False
                nic = {
                    "network": f"{workout_id}-{n['network']}",
                    "internal_IP": n['internal_IP'],
                    "subnet": f"{workout_id}-{n['network']}-{n['subnet']}",
                    "external_NAT": n['external_NAT']
                }
                # Nested VMs are sometimes used for vulnerable servers. This adds those specified IP addresses as
                # aliases to the NIC
                if 'IP_aliases' in n and n['IP_aliases']:
                    alias_ip_ranges = []
                    for ipaddr in n['IP_aliases']:
                        alias_ip_ranges.append({"ipCidrRange": ipaddr})
                    nic['aliasIpRanges'] = alias_ip_ranges
                nics.append(nic)
            # Add the startup script for assessment as metadata if it exists
            meta_data = None
            if startup_scripts and server['name'] in startup_scripts:
                meta_data = startup_scripts[server['name']]
            g_logger.log_struct(
                {
                    "message": "Building server {} for workout {}".format(server_name, workout_id)
                }, severity=LOG_LEVELS.INFO
            )
            create_instance_custom_image(compute=compute, workout=workout_id, name=server_name,
                                         custom_image=custom_image, machine_type=machine_type,
                                         networkRouting=network_routing, networks=nics, tags=tags,
                                         meta_data=meta_data, sshkey=sshkey, minCpuPlatform=min_cpu_platform,
                                         build_type=build_type, machine_image=machine_image, add_disk=add_disk,
                                         snapshot=snapshot, options=options)

        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_SERVERS)
    # Create the student entry guacamole server
    # TODO: There's a bug here when attempting to build the guacamole server
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_STUDENT_ENTRY):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_STUDENT_ENTRY)
        if workout['student_entry']:
            # A configuration may have multiple connections from the student entry to support multiple
            # concurrent students
            guac_connection = []
            if 'connections' in workout['student_entry']:
                network_name = f"{workout_id}-{workout['student_entry']['network']}"
                for entry in workout['student_entry']['connections']:
                    connection = create_guac_connection(workout_id, entry)
                    guac_connection.append(connection)
            else:
                network_name = f"{workout_id}-{workout['student_entry']['network']}"
                guac_connection.append(create_guac_connection(workout_id, workout['student_entry']))
            build_guacamole_server(build=workout, network=network_name,
                                   guacamole_connections=guac_connection)
            # Get the workout key again or the state transition will overwrite it
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        else:
            state_transition(entity=workout, new_state=BUILD_STATES.BROKEN)
            return
        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_STUDENT_ENTRY)
    # Create all of the network routes and firewall rules
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_ROUTES):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_ROUTES)
        g_logger.log_struct(
            {
                "message": "Creating network routes and firewall rules"
            }, severity=LOG_LEVELS.INFO
        )
        if 'routes' in workout and workout['routes']:
            workout_route_setup(workout_id)

    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_FIREWALL):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_FIREWALL)
        firewall_rules = []
        for rule in workout['firewall_rules']:
            firewall_rules.append({"name": "%s-%s" % (workout_id, rule['name']),
                                   "network": "%s-%s" % (workout_id, rule['network']),
                                   "targetTags": rule['target_tags'],
                                   "protocol": rule['protocol'],
                                   "ports": rule['ports'],
                                   "sourceRanges": rule['source_ranges']})
    
        create_firewall_rules(firewall_rules)
        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_FIREWALL)
