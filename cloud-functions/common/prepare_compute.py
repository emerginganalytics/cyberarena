import time
import calendar
import ipaddress
from google.cloud import pubsub_v1
from google.cloud import datastore
from googleapiclient import errors
from netaddr import IPAddress, IPNetwork

from common.globals import workout_globals, project, zone, dnszone, ds_client, compute, SERVER_STATES, SERVER_ACTIONS, \
    PUBSUB_TOPICS, guac_password, get_random_alphaNumeric_string, student_entry_image, BUILD_TYPES, log_client, \
    LOG_LEVELS, parent_project
from common.dns_functions import add_dns_record
from common.compute_management import get_server_ext_address, server_build
from common.networking_functions import create_firewall_rules


def process_server_options(server, options):
    """
    Process a list of options which may be included with the server.
    @param server:
    @type server: Datastore entry of type cybergym-server
    @param options: A list of available options for managing the build of the server
    @type options: List
    @return: server
    @rtype: Datastore entry
    """
    for option in options:
        if type(option) == str and option == "delayed_start":
            server["delayed_start"] = True



def get_student_entry_ip_address(workout, network):
    """
    Find the first available IP address to use for the student entry server.
    @param workout: Datastore entry for the workout
    @param network: The network name for the workout
    @return: An available IP address
    @rtype: str
    """
    workout_id = workout.key.name
    network = network.replace(f"{workout_id}-", '')
    ip_subnet = None
    for network_name in workout['networks']:
        if network_name['name'] == network:
            ip_subnet = IPNetwork(network_name['subnets'][0]['ip_subnet'])

    unavailable = []
    for server in workout['servers']:
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


def create_instance_custom_image(compute, workout, name, custom_image, machine_type,
                                 networkRouting, networks, tags, meta_data=None, sshkey=None, student_entry=False,
                                 minCpuPlatform=None, build_type=None, machine_image=None, add_disk=None,
                                 guacamole_startup_script=None, snapshot=None, options=None):
    """
    Core function to create a new server according to the input specification. This gets called through
    a cloud function during the automatic build
    :param compute: A compute object to build the server
    :param workout: The ID of the build
    :param name: Name of the server
    :param custom_image: Cloud image to use for the build
    :param machine_type: The cloud machine type
    :param networkRouting: True or False whether this is a firewall which routes traffic
    :param networks: The NIC specification for this server
    :param tags: Tags are key and value pairs which sometimes define the firewall rules
    :param meta_data: This includes startup scripts
    :param sshkey: If the server is running an SSH service, then this adds the public ssh key used for connections
    :param student_entry: If this is a student_entry image, then add that to the configuration.
    :param minCpuPlatform: For custom images
    :param build_type: Used for building off machine images
    :param machine_image: A designated machine image for the build
    :param add_disk: For adding additional disks to the build
    :param guacamole_startup_script: A workaround due to not being able to exclude_from_index nested fields in the
            Google API
    :param snapshot: Whether or not to snapshot the server
    :param options: A list of possible options to include in managing the server.
    :return: None
    """
    # First check to see if the server configuration already exists. If so, then return without error
    exists_check = ds_client.query(kind='cybergym-server')
    exists_check.add_filter("name", "=", name)
    g_logger = log_client.logger(str(name))
    g_logger.log_struct(
        {
            "message": "Attempting to build server"
        }, severity=LOG_LEVELS.INFO
    )
    if exists_check.fetch().num_results > 0:
        g_logger.log_struct(
            {
                "message": "Server already exists. Skipping configuration"
            }, severity=LOG_LEVELS.WARNING
        )
        return

    config = {}
    config['name'] = name
    if machine_type:
        config['machineType'] = "zones/%s/machineTypes/%s" % (zone, machine_type)
    if tags:
        config['tags'] = tags
    if build_type != BUILD_TYPES.MACHINE_IMAGE:
        image_response = compute.images().get(project=parent_project, image=custom_image).execute()
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

    if networks:
        networkInterfaces = []
        for network in networks:
            if network["external_NAT"]:
                accessConfigs = {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            else:
                accessConfigs = None
            add_network_interface = {
                'network': 'projects/%s/global/networks/%s' % (project, network["network"]),
                'subnetwork': 'regions/us-central1/subnetworks/' + network["subnet"],
                'accessConfigs': [
                    accessConfigs
                ]
            }
            if 'internal_IP' in network:
                add_network_interface['networkIP'] = network["internal_IP"]

            if 'aliasIpRanges' in network:
                add_network_interface['aliasIpRanges'] = network['aliasIpRanges']
            networkInterfaces.append(add_network_interface)
        config['networkInterfaces'] = networkInterfaces
    # Allow the instance to access cloud storage and logging.
    config['serviceAccounts'] =  [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]

    if meta_data:
        config['metadata'] = {'items': [meta_data]}
    if sshkey:
        if 'metadata' in config and config['metadata'] and 'items' in config['metadata']:
            config['metadata']['items'].append({"key": "ssh-keys", "value": sshkey})
        else:
            config['metadata'] = {'items': [{"key": "ssh-keys", "value": sshkey}]}

    if networkRouting:
        config["canIpForward"] = True

    if add_disk:
        try:
            image_config = {"name": name + "-disk", "sizeGb": add_disk,
                             "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}
            response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
                        "source": "projects/" + project + "/zones/" + zone + "/disks/" + name + "-disk"}
            config['disks'].append(new_disk)
        except errors.HttpError as err:
            # If the disk already exists (i.e. a nuke), then ignore
            if err.resp.status in [409]:
                pass

    if minCpuPlatform:
        config['minCpuPlatform'] = minCpuPlatform

    new_server = datastore.Entity(key=ds_client.key('cybergym-server', f'{name}'),
                                  exclude_from_indexes=['guacamole_startup_script'])

    new_server.update({
        'name': name,
        'workout': workout,
        'build_type': build_type,
        'machine_image': machine_image,
        'config': config,
        'state': SERVER_STATES.READY,
        'state-timestamp': str(calendar.timegm(time.gmtime())),
        'student_entry': student_entry,
        'guacamole_startup_script': guacamole_startup_script,
        'snapshot': snapshot
    })

    if options:
        process_server_options(new_server, options)

    try:
        ds_client.put(new_server)
    except:
        g_logger.log_struct(
            {
                "message": "Error storing server config"
            }, severity=LOG_LEVELS.WARNING
        )
        raise

    # Publish to a server build topic
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, pubsub_topic)
    future = publisher.publish(topic_path, data=b'Server Build', server_name=name, action=SERVER_ACTIONS.BUILD)

    # Used for debugging
    # server_build(name)


def build_guacamole_server(build, network, guacamole_connections, guac_ip_address=None):
    """
    Builds an image with an Apache Guacamole server and adds startup scripts to insert the
    correct users and connections into the guacamole database. This server becomes the entrypoint
    for all students in the arena.
    :param build: Build Entity for the workout or arena.
    :param network: The network name for the server
    :param guacamole_connections: An array of dictionaries for each student {workoutid, ip address of their server,
        and password for their server.
    :param guac_ip_address: The static IP address to assign the guacamole server. If this is not passed,
        then, an IP address if found.
    :return: Null
    """
    build_id = build.key.name
    g_logger = log_client.logger(build_id)
    multiple_users = False
    if 'unit_id' in build:
        unit = ds_client.get(ds_client.key('cybergym-unit', build['unit_id']))
        workout = ds_client.get(ds_client.key('cybergym-workout', build_id))
        if len(guacamole_connections) > 1 and unit["build_type"] != "arena":
            multiple_users = True
            workout["workout_credentials"] = []
    else:
        unit = build
    if len(guacamole_connections) == 0:
        return None
    startup_script = workout_globals.guac_startup_begin.format(guacdb_password=guac_password)

    i = 0
    ip = ""
    for connection in guacamole_connections:
        # Get a PRNG password for the workout and store it with the datastore record for display on the workout controller
        guac_user = 'cybergym' + str(i+1)
        guac_connection_password = get_random_alphaNumeric_string()
        ip = str(connection['ip'])
        if multiple_users:
            credential = {
                "workout_user": guac_user,
                "workout_password": guac_connection_password
            }
            workout["workout_credentials"].append(credential)
            connection_name = f"{build_id}-{i}"
            ds_client.put(workout)
        else:
            if unit['build_type'] == "arena":
                workout = ds_client.get(ds_client.key('cybergym-workout', connection['workout_id']))
            workout['workout_user'] = guac_user
            workout['workout_password'] = guac_connection_password
            connection_name = connection_name = f"{build_id}-{i}"
            ds_client.put(workout)

        safe_password = connection['password'].replace('$', '\$')
        safe_password = safe_password.replace("'", "\'")
        startup_script += workout_globals.guac_startup_user_add.format(user=guac_user,
                                                                       name=guac_user,
                                                                       guac_password=guac_connection_password)
        if connection['entry_type'] == 'vnc':
            startup_script += workout_globals.guac_startup_vnc.format(ip=connection['ip'],
                                                                      connection=connection_name,
                                                                      vnc_password=safe_password)
        else:
            startup_script += workout_globals.guac_startup_rdp.format(ip=connection['ip'],
                                                                      connection=connection_name,
                                                                      rdp_username=connection['username'],
                                                                      rdp_password=safe_password,
                                                                      security_mode=connection['security-mode'])
            if connection['domain']:
                startup_script += workout_globals.guac_startup_rdp_domain.format(domain=connection['domain'])
        startup_script += workout_globals.guac_startup_join_connection_user
        i += 1

    student_entry_ip = get_student_entry_ip_address(workout, network) if not guac_ip_address else guac_ip_address
    if not student_entry_ip:
        g_logger.log_struct(
            {
                "message": "Could not find available IP address for student entry guacamole server"
            }, severity=LOG_LEVELS.ERROR
        )
    startup_script += workout_globals.guac_startup_end
    server_name = "%s-%s" % (build_id, 'student-guacamole')
    tags = {'items': ['student-entry']}
    nics = [{
        "network": network,
        "subnet": "%s-%s" % (network, 'default'),
        "external_NAT": True,
        "internal_IP": student_entry_ip
    }]

    try:
        create_instance_custom_image(compute=compute, workout=build_id, name=server_name,
                                     custom_image=student_entry_image, machine_type='n1-standard-1',
                                     networkRouting=False, networks=nics, tags=tags, student_entry=True,
                                     guacamole_startup_script=startup_script)

        # Create the firewall rule allowing external access to the guacamole connection
        allow_entry = [
            {
                "name": "%s-%s" % (build_id, 'allow-student-entry'),
                "network": network,
                "targetTags": ['student-entry'],
                'protocol': None,
                'ports': ['tcp/80,8080,443'],
                'sourceRanges': ['0.0.0.0/0']
            }
        ]
        create_firewall_rules(allow_entry)
    except errors.HttpError as err:
        # 409 error means the server already exists.
        if err.resp.status in [409]:
            pass
        else:
            raise
