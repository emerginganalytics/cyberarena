import time
import calendar
from socket import timeout
import requests

from common.globals import project, zone, dnszone, ds_client, compute, SERVER_STATES, BUILD_STATES, workout_globals
from google.cloud import datastore
from googleapiclient.errors import HttpError
from common.dns_functions import add_dns_record, delete_dns
from common.state_transition import state_transition
from requests.exceptions import ConnectionError


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
    max_attempts = 10
    attempts = 0

    success = False
    while not success and attempts < max_attempts:
        try:
            requests.get(f"http://{ip_address}:8080/guacamole/#", timeout=40)
            return True
        except requests.exceptions.Timeout:
            attempts += 1
        except ConnectionError:
            print(f"HTTP Connection Error for Guacamole Server {ip_address}")
            attempts += 1
    return False


def register_student_entry(build_id, server_name):
    build = ds_client.get(ds_client.key('cybergym-workout', build_id))
    if not build:
        build = ds_client.get(ds_client.key('cybergym-unit', build_id))
    # Add the external_IP address for the workout. This allows easy deletion of the DNS record when deleting the arena
    ip_address = get_server_ext_address(server_name)
    add_dns_record(build_id, ip_address)
    # Make sure the guacamole server actually comes up successfully before setting the workout state to ready
    print(f"DNS record set for {server_name}. Now Testing guacamole connection. This may take a few minutes.")
    if test_guacamole(ip_address):
        # Now, since this is the guacamole server, update the state of the workout to READY
        print(f"Setting the build {build_id} to ready")
        state_transition(entity=build, new_state=BUILD_STATES.READY)
    else:
        state_transition(entity=build, new_state=BUILD_STATES.GUACAMOLE_SERVER_LOAD_TIMEOUT)

    # Return the IP address used for the server build function to set the server datastore element
    return ip_address


def check_build_state_change(build_id, check_server_state, change_build_state):
    query_workout_servers = ds_client.query(kind='cybergym-server')
    query_workout_servers.add_filter("workout", "=", build_id)
    for check_server in list(query_workout_servers.fetch()):
        if check_server['state'] != check_server_state:
            return
    # If we've made it this far, then all of the servers have changed to the desired state.
    # now we can change the entire state.
    build = ds_client.get(ds_client.key('cybergym-workout', build_id))
    if not build:
        build = ds_client.get(ds_client.key('cybergym-unit', build_id))
    state_transition(build, change_build_state)


def server_build(server_name):
    """
    Builds an individual server based on the specification in the Datastore entity with name server_name.
    :param server_name: The Datastore entity name of the server to build
    :return: A boolean status on the success of the build
    """
    print(f'Building server {server_name}')
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    state_transition(entity=server, new_state=SERVER_STATES.BUILDING)

    # Commented because this is only for Fortinet right now.
    # if 'canIPForward' in server and server['config']['canIpForward']:
    #     image_config = {"name": server_name + "-disk", "sizeGb": 30,
    #                     "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}
    #     response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
    #     compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

    # Begin the server build and keep trying for a bounded number of additional 30-second cycles
    i = 0
    build_success = False
    while not build_success and i < 5:
        workout_globals.refresh_api()
        try:
            response = compute.instances().insert(project=project, zone=zone, body=server['config']).execute()
            build_success = True
            print(f'Sent job to build {server_name}, and waiting for response')
        except BrokenPipeError:
            i += 1
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
        ip_address = register_student_entry(server['workout'], server_name)
        server['external_ip'] = ip_address
        ds_client.put(server)
        server = ds_client.get(ds_client.key('cybergym-server', server_name))

    # Now stop the server before completing
    print(f'Stopping {server_name}')
    compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
    state_transition(entity=server, new_state=SERVER_STATES.STOPPED)

    # If no other servers are building, then set the workout to the state of READY.
    build_id = server['workout']
    check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.STOPPED,
                             change_build_state=BUILD_STATES.READY)


def server_start(server_name):
    """
    Starts a server based on the specification in the Datastore entity with name server_name. A guacamole server
    is also registered with DNS.
    :param server_name: The Datastore entity name of the server to start
    :return: A boolean status on the success of the start
    """
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    state_transition(entity=server, new_state=SERVER_STATES.STARTING)

    # Begin the server start and keep trying for a bounded number of cycles
    i = 0
    start_success = False
    while not start_success and i < 5:
        workout_globals.refresh_api()
        try:
            response = compute.instances().start(project=project, zone=zone, instance=server_name).execute()
            start_success = True
            print(f'Sent job to start {server_name}, and waiting for response')
        except BrokenPipeError:
            i += 1

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
        ip_address = register_student_entry(server['workout'], server_name)
        server['external_ip'] = ip_address

    state_transition(entity=server, new_state=SERVER_STATES.RUNNING)
    print(f"Finished starting {server_name}")

    # If all servers have started, then change the build state
    build_id = server['workout']
    check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.RUNNING,
                             change_build_state=BUILD_STATES.RUNNING)
    return True


def server_delete(server_name):
    server = ds_client.get(ds_client.key('cybergym-server', server_name))

    state_transition(entity=server, new_state=SERVER_STATES.DELETING)
    workout_globals.refresh_api()
    try:
        response = compute.instances().delete(project=project, zone=zone, instance=server_name).execute()
    except HttpError as exception:
        # If the server is already deleted or no longer exists,
        state_transition(entity=server, new_state=SERVER_STATES.DELETED)
        print(f"Finished deleting {server_name}")

        # If all servers in the workout have been deleted, then set the workout state to True
        build_id = server['workout']
        check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.DELETED,
                                 change_build_state=BUILD_STATES.COMPLETED_DELETING_SERVERS)
        return True
    print(f'Sent delete request to {server_name}, and waiting for response')
    i = 0
    success = False
    while not success and i < 5:
        try:
            print(f"Begin waiting for delete response from operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            print('Response timeout for deleting server. Trying again')
            pass
    if not success:
        print(f'Timeout in trying to delete server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False

    # If this is a student entry server, delete the DNS
    if 'student_entry' in server and server['student_entry']:
        print(f'Deleting DNS record for {server_name}')
        ip_address = server['external_ip']
        delete_dns(server['workout'], ip_address)

    state_transition(entity=server, new_state=SERVER_STATES.DELETED)
    print(f"Finished deleting {server_name}")

    # If all servers in the workout have been deleted, then set the workout state to True
    build_id = server['workout']
    check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.DELETED,
                             change_build_state=BUILD_STATES.COMPLETED_DELETING_SERVERS)
    return True

def server_stop(server_name):
    server = ds_client.get(ds_client.key('cybergym-server', server_name))

    state_transition(entity=server, new_state=SERVER_STATES.STOPPING)

    i = 0
    stop_success = False
    while not stop_success and i < 5:
        workout_globals.refresh_api()
        try:
            response = compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
            stop_success = True
            print(f'Sent job to start {server_name}, and waiting for response')
            return True
        except BrokenPipeError:
            i += 1
    
    return False
