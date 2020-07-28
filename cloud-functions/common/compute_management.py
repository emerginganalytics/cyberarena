import time
import calendar
from socket import timeout

from common.globals import project, zone, dnszone, ds_client, compute, SERVER_STATES
from google.cloud import datastore
from common.dns_functions import add_dns_record, register_workout_server
from common.state_transition import state_transition


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


def server_build(server_name):
    """
    Builds an individual server based on the specification in the Datastore entity with name server_name.
    :param server_name: The Datastore entity name of the server to build
    :return: A boolean status on the success of the build
    """
    print(f'Building server {server_name}')
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    server_ready = state_transition(entity=server, new_state=SERVER_STATES.BUILDING,
                                           existing_state=SERVER_STATES.READY)
    if not server_ready:
        return False

    # If the server is a router, then add a disk for logging. Admittedly, this is for Fortinet firewalls
    if 'canIPForward' in server and server['config']['canIpForward']:
        image_config = {"name": server_name + "-disk", "sizeGb": 30,
                        "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}
        response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

    # Begin the server build and keep trying for an additional 2 30-second cycles
    response = compute.instances().insert(project=project, zone=zone, body=server['config']).execute()
    print(f'Sent job to build {server_name}, and waiting for response')
    i = 0
    success = False
    while not success and i < 2:
        try:
            print(f"Begin waiting for operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            print('Response timeout. Trying again')
            pass

    if success:
        print(f'Successfully built server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.RUNNING, existing_state=SERVER_STATES.BUILDING)
    else:
        print(f'Timeout in trying to build server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False

    # Now stop the server before completing
    print(f'Stopping {server_name}')
    compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
    state_transition(entity=server, new_state=SERVER_STATES.STOPPED)

# server_build('name=mtzmizsvmw-student-guacamole')

# def server_start():
#
#
# def server_delete():
#
#
# def server_reload():