import time
import calendar
from socket import timeout
import requests
from googleapiclient import discovery

from common.globals import project, zone, dnszone, ds_client, compute, SERVER_STATES, BUILD_STATES, \
    workout_globals, BUILD_TYPES, log_client, gcp_operation_wait, PUBSUB_TOPICS, SERVER_ACTIONS, cloud_log,\
    LOG_LEVELS, LogIDs
from google.cloud import pubsub_v1
from googleapiclient.errors import HttpError
from common.dns_functions import add_dns_record, delete_dns
from common.state_transition import state_transition
from requests.exceptions import ConnectionError
from common.publish_compute_image import create_production_image, create_snapshot_from_disk

def get_server_ext_address(server_name):
    """
    Provides the IP address of a given server name. Right now, this is used for managing DNS entries.
    :param server_name: The server name in the cloud project
    :return: The IP address of the server or throws an error
    """
    g_logger = log_client.logger(str(server_name))
    try:
        new_instance = compute.instances().get(project=project, zone=zone, instance=server_name).execute()
        ip_address = new_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    except KeyError:
        g_logger.log_text('Server %s does not have an external IP address' % server_name)
        return False
    return ip_address


def test_guacamole(ip_address, build_id=None):
    max_attempts = 15
    attempts = 0
    g_logger = log_client.logger(str(build_id))
    success = False
    while not success and attempts < max_attempts:
        try:
            requests.get(f"http://{ip_address}:8080/guacamole/#", timeout=40)
            return True
        except requests.exceptions.Timeout:
            g_logger.log_text(f"Build {build_id}: Timeout {attempts} waiting for guacamole server connection.")
            attempts += 1
        except ConnectionError:
            g_logger.log_text(f"HTTP Connection Error for Guacamole Server {ip_address}")
            attempts += 1
    return False


def register_student_entry(build_id, server_name):
    build = ds_client.get(ds_client.key('cybergym-workout', build_id))
    if not build:
        build = ds_client.get(ds_client.key('cybergym-unit', build_id))
    g_logger = log_client.logger(str(build_id))

    # Add the external_IP address for the workout. This allows easy deletion of the DNS record when deleting the arena
    ip_address = get_server_ext_address(server_name)
    add_dns_record(build_id, ip_address)
    # Make sure the guacamole server actually comes up successfully before setting the workout state to ready
    g_logger.log_text(f"DNS record set for {server_name}. Now Testing guacamole connection. This may take a few minutes.")
    if test_guacamole(ip_address, build_id):
        # Now, since this is the guacamole server, update the state of the workout to READY
        g_logger.log_text(f"Setting the build {build_id} to ready")
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
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    build_id = server['workout']
    g_logger = log_client.logger(str(server_name))
    state_transition(entity=server, new_state=SERVER_STATES.BUILDING)
    config = server['config'].copy()
    nested_vm = server.get("nested_virtualization", False)
    if nested_vm:
        config['advancedMachineFeatures'] = {"enableNestedVirtualization": nested_vm}


    """
    Currently, we need a workaround to insert the guacamole startup script because of a 1500 character limit on
    indexed fields. The exclude_from_index does not work on embedded datastore fields
    """
    if 'student_entry' in server and server['student_entry']:
        config['metadata'] = {'items': [{"key": "startup-script", "value": server['guacamole_startup_script']}]}


    # Begin the server build and keep trying for a bounded number of additional 30-second cycles
    i = 0
    build_success = False
    while not build_success and i < 5:
        workout_globals.refresh_api()
        try:
            if server.get('add_disk', None):
                try:
                    image_config = {"name": server_name + "-disk", "sizeGb": server['add_disk'],
                                    "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}
                    response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
                    compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
                except HttpError as err:
                    # If the disk already exists (i.e. a nuke), then ignore
                    if err.resp.status in [409]:
                        pass
            if server['build_type'] == BUILD_TYPES.MACHINE_IMAGE:
                source_machine_image = f"projects/{project}/global/machineImages/{server['machine_image']}"
                compute_beta = discovery.build('compute', 'beta')
                response = compute_beta.instances().insert(project=project, zone=zone, body=config,
                                                           sourceMachineImage=source_machine_image).execute()
            else:
                if "delayed_start" in server and server["delayed_start"]:
                    time.sleep(30)
                response = compute.instances().insert(project=project, zone=zone, body=config).execute()
            build_success = True
            g_logger.log_text(f'Sent job to build {server_name}, and waiting for response')
        except BrokenPipeError:
            i += 1
        except HttpError as exception:
            cloud_log(build_id, f"Error when trying to build {server_name}: {exception.reason}", LOG_LEVELS.ERROR)
            return False
    i = 0
    success = False
    while not success and i < 5:
        try:
            g_logger.log_text(f"Begin waiting for build operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            g_logger.log_text('Response timeout for build. Trying again')
            pass

    if success:
        g_logger.log_text(f'Successfully built server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.RUNNING, existing_state=SERVER_STATES.BUILDING)
    else:
        g_logger.log_text(f'Timeout in trying to build server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False

    # If this is a student entry server, register the DNS
    if 'student_entry' in server and server['student_entry']:
        g_logger.log_text(f'Setting DNS record for {server_name}')
        ip_address = register_student_entry(server['workout'], server_name)
        server['external_ip'] = ip_address
        ds_client.put(server)
        server = ds_client.get(ds_client.key('cybergym-server', server_name))

    # Now stop the server before completing
    g_logger.log_text(f'Stopping {server_name}')
    compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
    state_transition(entity=server, new_state=SERVER_STATES.STOPPED)

    # If no other servers are building, then set the workout to the state of READY.
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
    g_logger = log_client.logger(str(server_name))
    # Begin the server start and keep trying for a bounded number of cycles
    i = 0
    start_success = False
    while not start_success and i < 5:
        workout_globals.refresh_api()
        try:
            if "delayed_start" in server and server["delayed_start"]:
                time.sleep(30)
            response = compute.instances().start(project=project, zone=zone, instance=server_name).execute()
            start_success = True
            g_logger.log_text(f'Sent job to start {server_name}, and waiting for response')
        except BrokenPipeError:
            i += 1

    g_logger.log_text(f'Sent start request to {server_name}, and waiting for response')
    i = 0
    success = False
    while not success and i < 5:
        try:
            g_logger.log_text(f"Begin waiting for start response from operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            g_logger.log_text('Response timeout for starting server. Trying again')
            pass
    if not success:
        g_logger.log_text(f'Timeout in trying to start server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False
    # If this is the guacamole server for student entry, then register the new DNS
    if 'student_entry' in server and server['student_entry']:
        g_logger.log_text(f'Setting DNS record for {server_name}')
        ip_address = register_student_entry(server['workout'], server_name)
        server['external_ip'] = ip_address

    state_transition(entity=server, new_state=SERVER_STATES.RUNNING)
    g_logger.log_text(f"Finished starting {server_name}")

    # If all servers have started, then change the build state
    build_id = server['workout']
    check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.RUNNING,
                             change_build_state=BUILD_STATES.RUNNING)
    return True


def server_delete(server_name):
    g_logger = log_client.logger(str(server_name))
    server_list = list(ds_client.query(kind='cybergym-server').add_filter('name', '=', str(server_name)).fetch())
    server_is_deleted = list(ds_client.query(kind='cybergym-server')
                             .add_filter('name', '=', str(server_name)).add_filter('state', '=', 'DELETED').fetch())
    if server_is_deleted and server_list:
        g_logger.log_text(f'Server "' + server_name + '" has already been deleted.')
        return True
    elif not server_list:
        g_logger.log_text(f'Server of name "' + server_name + '" does not exist in datastore, unable to Delete.')
        return True
    else:
        server = ds_client.get(ds_client.key('cybergym-server', server_name))

    state_transition(entity=server, new_state=SERVER_STATES.DELETING)
    # If there are snapshots associated with this server, then delete the snapshots.
    if 'snapshot' in server and server['snapshot']:
        Snapshot.delete_snapshot(server_name)

    workout_globals.refresh_api()
    try:
        response = compute.instances().delete(project=project, zone=zone, instance=server_name).execute()
    except HttpError as exception:
        # If the server is already deleted or no longer exists,
        state_transition(entity=server, new_state=SERVER_STATES.DELETED)
        g_logger.log_text(f"Finished deleting {server_name}")

        # If all servers in the workout have been deleted, then set the workout state to True
        build_id = server['workout']
        check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.DELETED,
                                 change_build_state=BUILD_STATES.COMPLETED_DELETING_SERVERS)
        return True
    g_logger.log_text(f'Sent delete request to {server_name}, and waiting for response')
    i = 0
    success = False
    while not success and i < 5:
        try:
            g_logger.log_text(f"Begin waiting for delete response from operation {response['id']}")
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            success = True
        except timeout:
            i += 1
            g_logger.log_text('Response timeout for deleting server. Trying again')
            pass
    if not success:
        g_logger.log_text(f'Timeout in trying to delete server {server_name}')
        state_transition(entity=server, new_state=SERVER_STATES.BROKEN)
        return False

    # If this is a student entry server, delete the DNS
    if 'student_entry' in server and server['student_entry']:
        g_logger.log_text(f'Deleting DNS record for {server_name}')
        ip_address = server['external_ip']
        delete_dns(server['workout'], ip_address)

    state_transition(entity=server, new_state=SERVER_STATES.DELETED)
    g_logger.log_text(f"Finished deleting {server_name}")

    # If all servers in the workout have been deleted, then set the workout state to True
    build_id = server['workout']
    check_build_state_change(build_id=build_id, check_server_state=SERVER_STATES.DELETED,
                             change_build_state=BUILD_STATES.COMPLETED_DELETING_SERVERS)
    return True

def server_stop(server_name):
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    g_logger = log_client.logger(str(server_name))
    state_transition(entity=server, new_state=SERVER_STATES.STOPPING)

    i = 0
    stop_success = False
    while not stop_success and i < 5:
        workout_globals.refresh_api()
        try:
            response = compute.instances().stop(project=project, zone=zone, instance=server_name).execute()
            stop_success = True
            g_logger.log_text(f'Sent job to start {server_name}, and waiting for response')
            return True
        except BrokenPipeError:
            i += 1
    
    return False

def server_rebuild(server_name):
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    g_logger = log_client.logger(str(server_name))
    g_logger.log_text(f"Rebuilding server {server_name}")
    if 'state' in server:
        if server['state'] == 'RUNNING':
            server_stop(server_name)
    server_delete(server_name)

    server_build(server_name)


class Snapshot:
    """
    Used for managing snapshot for workouts.
    """
    def __init__(self):
        pass

    @staticmethod
    def snapshot_all():
        """
        Query all workouts over the past 4 months that have not been deleted and take a snapshot of each server where
        indicated.
        @return:
        @rtype:
        """
        query_workouts = ds_client.query(kind='cybergym-workout')
        query_workouts.add_filter('active', '=', True)
        for workout in list(query_workouts.fetch()):
            workout_project = workout.get('build_project_location', project)
            if workout_project == project:
                if 'state' in workout and workout['state'] != BUILD_STATES.DELETED:
                    query_workout_servers = ds_client.query(kind='cybergym-server')
                    query_workout_servers.add_filter("workout", "=", workout.key.name)
                    for server in list(query_workout_servers.fetch()):
                        snapshot = server.get('snapshot', None)
                        if snapshot:
                            pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
                            publisher = pubsub_v1.PublisherClient()
                            topic_path = publisher.topic_path(project, pubsub_topic)
                            publisher.publish(topic_path, data=b'Server Snapshot', server_name=server['name'],
                                              action=SERVER_ACTIONS.SNAPSHOT)

    @staticmethod
    def snapshot_server(server_name):
        """
        Takes a snapshot of the server with name server_name.
        @param server_name: The name of the server to snapshot
        @type server_name: String
        @return: None
        """
        create_snapshot_from_disk(server_name, max_snapshots=1)

    @staticmethod
    def restore_server(server_name):
        """
        1) Delete the server, 2) Set the image name to be one previously snapshotted, 3) Build the server, and then
        4) restore the build configuration to the existing image in case it's later nuked.
        @param server_name: Name of the server.
        @type server_name: String
        @return: None
        """
        server_delete(server_name)

        server = ds_client.get(ds_client.key('cybergym-server', server_name))
        snapshots = compute.snapshots().list(project=project, filter=f"name = {server.key.name}*").execute()
        snapshot_name = snapshots['items'][0]['name']
        sourceSnapshot = f"projects/ualr-cybersecurity/global/snapshots/{snapshot_name}"
        disks = [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceSnapshot': sourceSnapshot,
                }
            }
        ]
        old_config_disks = server['config']['disks']
        server['config']['disks'] = disks
        ds_client.put(server)
        server_build(server_name)
        # Now restore the old image config in case the user might later need to nuke the workout.
        server['config']['disks'] = old_config_disks
        ds_client.put(server)

    @staticmethod
    def delete_snapshot(server_name):
        """
        As part of the workout deletion, deletes any associated server snapshots and images
        @param server_name: Name of the server snapshot to delete
        @type server_name: String
        @return: None
        """
        i = 0
        delete_success = False
        nothing_to_delete = False
        while not delete_success and i < 5 and not nothing_to_delete:
            try:
                response = compute.snapshots().list(project=project, filter=f"name = {server_name}*").execute()
                for snapshot in response['items']:
                    compute.snapshots().delete(project=project, snapshot=snapshot['name']).execute()
                delete_success = True
            except HttpError:
                nothing_to_delete = True
            except BrokenPipeError:
                i += 1
        if not delete_success and not nothing_to_delete:
            raise Exception(f"Error deleting snapshot image-{server_name}")