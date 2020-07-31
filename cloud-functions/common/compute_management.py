import time
import calendar
from socket import timeout
import requests

from common.globals import project, zone, dnszone, ds_client, compute, SERVER_STATES, BUILD_STATES
from google.cloud import datastore
from googleapiclient.errors import HttpError
from common.dns_functions import add_dns_record
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


def test_guacamole(ip_address):
    max_attempts = 40
    attempts = 0
    sleeptime = 5  # in seconds, no reason to continuously try if network is down

    # while true: #Possibly Dangerous
    success = False
    while not success and attempts < max_attempts:
        time.sleep(sleeptime)
        try:
            requests.get(f"http://{ip_address}:8080/guacamole/#", timeout=5)
            return True
        except requests.exceptions.Timeout:
            attempts += 1
    return False


def register_student_entry(build_id, server_name):
    build = ds_client.get(ds_client.key('cybergym-workout', build_id))
    if not build:
        build = ds_client.get(ds_client.key('cybergym-unit', build_id))
    # Add the external_IP address for the workout. This allows easy deletion of the DNS record when deleting the arena
    ip_address = get_server_ext_address(server_name)
    add_dns_record(build_id, ip_address)
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    server['external_ip'] = ip_address
    ds_client.put(server)
    # Make sure the guacamole server actually comes up successfully before setting the workout state to ready
    if test_guacamole(ip_address):
        # Now, since this is the guacamole server, update the state of the workout to READY
        print(f"Setting the build {build_id} to ready")
        state_transition(entity=build, new_state=BUILD_STATES.READY)
    else:
        state_transition(entity=build, new_state=BUILD_STATES.GUACAMOLE_SERVER_LOAD_TIMEOUT)


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
    while not success and i < 5:
        try:
            print(f"Begin waiting for build operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            print('Response timeout for build. Trying again')
            pass

    if success:
        print(f'Successfully built server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.RUNNING, existing_state=SERVER_STATES.BUILDING)
    else:
        print(f'Timeout in trying to build server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False

    # If this is a student entry server, register the DNS
    if 'student_entry' in server and server['student_entry']:
        print(f'Setting DNS record for {server_name}')
        register_student_entry(server['workout'], server_name)

    # Now stop the server before completing
    print(f'Stopping {server_name}')
    compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
    state_transition(entity=server, new_state=SERVER_STATES.STOPPED)


def server_start(server_name):
    """
    Starts a server based on the specification in the Datastore entity with name server_name. A guacamole server
    is also registered with DNS.
    :param server_name: The Datastore entity name of the server to start
    :return: A boolean status on the success of the start
    """
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    state_transition(entity=server, new_state=SERVER_STATES.STARTING)
    response = compute.instances().start(project=project, zone=zone, instance=server_name).execute()
    print(f'Sent start request to {server_name}, and waiting for response')
    i = 0
    success = False
    while not success and i < 5:
        try:
            print(f"Begin waiting for start response from operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            print('Response timeout for starting server. Trying again')
            pass
    if not success:
        print(f'Timeout in trying to start server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False
    # If this is the guacamole server for student entry, then register the new DNS
    if 'student_entry' in server and server['student_entry']:
        print(f'Setting DNS record for {server_name}')
        register_student_entry(server['workout'], server_name)

    state_transition(entity=server, new_state=SERVER_STATES.RUNNING)
    print(f"Finished starting {server_name}")
    return True

#
#
# def server_delete():
#
#
# def server_reload():

server_start('hadomrzbkz-student-guacamole')