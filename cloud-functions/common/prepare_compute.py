import time
import calendar
import ipaddress
from google.cloud import pubsub_v1
from google.cloud import datastore
from googleapiclient import errors

from common.globals import workout_globals, project, zone, dnszone, ds_client, compute, SERVER_STATES, SERVER_ACTIONS, \
    PUBSUB_TOPICS, guac_password, get_random_alphaNumeric_string, student_entry_image
from common.dns_functions import add_dns_record
from common.compute_management import get_server_ext_address, server_build
from common.networking_functions import create_firewall_rules


def create_instance_custom_image(compute, workout, name, custom_image, machine_type,
                                 networkRouting, networks, tags, meta_data, sshkey=None, student_entry=False,
                                 minCpuPlatform=None):
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
    :return: None
    """
    # First check to see if the server configuration already exists. If so, then return without error
    exists_check = ds_client.query(kind='cybergym-server')
    exists_check.add_filter("name", "=", name)
    if exists_check.fetch().num_results > 0:
        print(f'Server {name} already exists. Skipping configuration')
        return

    image_response = compute.images().get(project=project, image=custom_image).execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine = "zones/%s/machineTypes/%s" % (zone, machine_type)

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
    config = {
        'name': name,
        'machineType': machine,

        # allow http and https server with tags
        'tags': tags,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        'networkInterfaces': networkInterfaces,
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
    }

    if meta_data:
        config['metadata'] = {'items': [meta_data]}
    if sshkey:
        if 'metadata' in config and config['metadata'] and 'items' in config['metadata']:
            config['metadata']['items'].append({"key": "ssh-keys", "value": sshkey})
        else:
            config['metadata'] = {'items': [{"key": "ssh-keys", "value": sshkey}]}

    # For a network routing firewall (i.e. Fortinet) add an additional disk for logging.
    if networkRouting:
        config["canIpForward"] = True
        # Commented out because only Fortinet uses this. Need to create a custom build template instead.
        # new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
        #              "source": "projects/" + project + "/zones/" + zone + "/disks/" + name + "-disk"}
        # config['disks'].append(new_disk)

    if minCpuPlatform:
        config['minCpuPlatform'] = minCpuPlatform

    new_server = datastore.Entity(ds_client.key('cybergym-server', f'{name}'))

    new_server.update({
        'name': name,
        'workout': workout,
        'config': config,
        'state': SERVER_STATES.READY,
        'state-timestamp': str(calendar.timegm(time.gmtime())),
        'student_entry': student_entry
    })
    ds_client.put(new_server)

    # Publish to a server build topic
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, pubsub_topic)
    future = publisher.publish(topic_path, data=b'Server Build', server_name=name, action=SERVER_ACTIONS.BUILD)
    print(future.result())
    # The command below is used for testing
    # server_build(name)


def build_guacamole_server(build, network, guacamole_connections):
    """
    Builds an image with an Apache Guacamole server and adds startup scripts to insert the
    correct users and connections into the guacamole database. This server becomes the entrypoint
    for all students in the arena.
    :param type: Either workout or arena build.
    :param build: Build Entity for the workout or arena.
    :param network: The network name for the server
    :param guacamole_connections: An array of dictionaries for each student {workoutid, ip address of their server,
        and password for their server.
    :return: Null
    """
    build_id = build.key.name
    if len(guacamole_connections) == 0:
        return None

    startup_script = workout_globals.guac_startup_begin.format(guacdb_password=guac_password)
    i = 0
    for connection in guacamole_connections:
        # Get a PRNG password for the workout and store it with the datastore record for display on the workout controller
        guac_user = 'cybergym' + str(i+1)
        guac_connection_password = get_random_alphaNumeric_string()
        workout = ds_client.get(ds_client.key('cybergym-workout', connection['workout_id']))
        workout['workout_user'] = guac_user
        workout['workout_password'] = guac_connection_password
        ds_client.put(workout)

        safe_password = connection['password'].replace('$', '\$')
        safe_password = safe_password.replace("'", "\'")
        startup_script += workout_globals.guac_startup_user_add.format(user=guac_user,
                                                                       name=guac_user,
                                                                       guac_password=guac_connection_password)
        if connection['entry_type'] == 'vnc':
            startup_script += workout_globals.guac_startup_vnc.format(ip=connection['ip'],
                                                                      connection=connection['workout_id'],
                                                                      vnc_password=safe_password)
        else:
            startup_script += workout_globals.guac_startup_rdp.format(ip=connection['ip'],
                                                                      connection=connection['workout_id'],
                                                                      rdp_username=connection['username'],
                                                                      rdp_password=safe_password,
                                                                      security_mode=connection['security-mode'])
            if connection['domain']:
                startup_script += workout_globals.guac_startup_rdp_domain.format(domain=connection['domain'])
        startup_script += workout_globals.guac_startup_join_connection_user
        i += 1
    startup_script += workout_globals.guac_startup_end

    server_name = "%s-%s" % (build_id, 'student-guacamole')
    tags = {'items': ['student-entry']}
    nics = [{
        "network": network,
        "subnet": "%s-%s" % (network, 'default'),
        "external_NAT": True
    }]
    meta_data = {"key": "startup-script", "value": startup_script}
    try:
        create_instance_custom_image(compute=compute, workout=build_id, name=server_name,
                                     custom_image=student_entry_image, machine_type='n1-standard-1',
                                     networkRouting=False, networks=nics, tags=tags,
                                     meta_data=meta_data, sshkey=None, student_entry=True)

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
