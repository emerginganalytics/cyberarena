import time
from socket import timeout

from common.globals import project, zone, dnszone, ds_client, compute
from common.dns_functions import add_dns_record, register_workout_server


def create_instance_custom_image(compute, workout, name, custom_image, machine_type,
                                 networkRouting, networks, tags, meta_data, sshkey=None, guac_path=None):
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
    :param guac_path: A guacamole path if this is a lab entry server. This will soon deprecate, hopefully
    :return: None
    """
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
            'networkIP': network["internal_IP"],
            'accessConfigs': [
                accessConfigs
            ]
        }
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
        config['metadata'] = meta_data
    if sshkey:
        if 'items' in meta_data:
            config['metadata']['items'].append({"key": "ssh-keys", "value": sshkey})
        else:
            config['metadata'] = {'items': {"key": "ssh-keys", "value": sshkey}}

    # For a network routing firewall (i.e. Fortinet) add an additional disk for logging.
    if networkRouting:
        config["canIpForward"] = True
        image_config = {"name": name + "-disk", "sizeGb": 30,
                        "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}

        response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

        new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
                     "source": "projects/" + project + "/zones/" + zone + "/disks/" + name + "-disk"}
        config['disks'].append(new_disk)

    response = compute.instances().insert(project=project, zone=zone, body=config).execute()
    try:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
    except timeout:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

    if tags:
        if 'items' in tags:
            for item in tags['items']:
                if item == 'labentry':
                    ip_address = get_server_ext_address(name)
                    add_dns_record(workout, ip_address)
                    key = ds_client.key('cybergym-workout', workout)
                    build = ds_client.get(key)
                    build["external_ip"] = ip_address
                    ds_client.put(build)

    if guac_path:
        register_workout_server(workout, name, guac_path)


def get_server_ext_address(server_name):
    """
    Provides the IP address of a given server name. Right now, this is used for managing DNS entries.
    :param server_name: The server name in the cloud project
    :return: The IP address of the server or throws an error
    """

    try:
        new_instance = compute.instances().get(project=project, zone=zone, instance=server_name).execute()
        ip_address = new_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    except KeyError:
        print('Server %s does not have an external IP address' % server_name)
        return False
    return ip_address