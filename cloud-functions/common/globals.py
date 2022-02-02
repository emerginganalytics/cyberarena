import random
import string
import time
import calendar
import googleapiclient.discovery
from google.cloud import runtimeconfig, datastore, storage
from google.cloud import logging as g_logging
from googleapiclient.errors import HttpError
from socket import timeout


runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
mysql_ip = myconfig.get_variable('sql_ip')
mysql_ip = mysql_ip.value.decode("utf-8") if mysql_ip else None
project = myconfig.get_variable('project').value.decode("utf-8")
region = myconfig.get_variable('region').value.decode("utf-8")
zone = myconfig.get_variable('zone').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
script_repository = myconfig.get_variable('script_repository').value.decode("utf-8")
custom_dnszone = myconfig.get_variable('dnszone')
dnszone = custom_dnszone.value.decode("utf-8") if custom_dnszone else 'cybergym-public'
custom_main_app_url = myconfig.get_variable('main_app_url')
main_app_url = custom_main_app_url.value.decode("utf-8") if custom_main_app_url \
    else 'https://buildthewarrior.cybergym-eac-ualr.org'
parent_project = myconfig.get_variable('parent_project')
parent_project = parent_project.value.decode("utf-8") if parent_project else project
student_instructions_url = myconfig.get_variable('student_instructions_url')
student_instructions_url = student_instructions_url.value.decode("utf-8") if student_instructions_url else \
    'https://storage.googleapis.com/student_workout_instructions_ualr-cybersecurity/'
teacher_instructions_url = myconfig.get_variable('teacher_instructions_url')
teacher_instructions_url = teacher_instructions_url.value.decode("utf-8") if teacher_instructions_url else \
    'https://storage.googleapis.com/teacher_workout_instructions_ualr-cybersecurity/'

# Set the GCP Objects
ds_client = datastore.Client(project=parent_project)
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
log_client = g_logging.Client()

workout_token = 'RG987S1GVNKYRYHYA'
student_entry_image = 'image-labentry'

# Use this for debugging. Uncomment the above endpoint for final environment.
post_endpoint = 'http://localhost:8080/complete'


class workout_globals():
    MAX_RUN_HOURS = 10
    yaml_bucket = project + '_cloudbuild'
    yaml_folder = 'yaml-build-files/'

    @staticmethod
    def extended_wait(project, zone, operation_id):
        max_wait = 3
        i = 0
        complete = False
        while not complete and i <= max_wait:
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=operation_id).execute()
                complete = True
            except:
                i += 1

        if not complete:
            print("Timeout for operation %s" % operation_id)
            return False
        else:
            return True

    @staticmethod
    def refresh_api():
        compute = googleapiclient.discovery.build('compute', 'v1')
        return compute


class SERVER_STATES:
    READY = 'READY'
    BUILDING = 'BUILDING'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    STOPPED = 'STOPPED'
    EXPIRED = 'EXPIRED'
    MISFIT = 'MISFIT'
    RESETTING = 'RESETTING'
    RELOADING = 'RELOADING'
    BROKEN = 'BROKEN'
    DELETING = 'DELETING'
    DELETED = 'DELETED'


class BUILD_STATES:
    START = 'START'
    BUILDING_ASSESSMENT = 'BUILDING_ASSESSMENT'
    BUILDING_NETWORKS = 'BUILDING_NETWORKS'
    COMPLETED_NETWORKS = 'COMPLETED_NETWORKS'
    BUILDING_SERVERS = 'BUILDING_SERVERS'
    COMPLETED_SERVERS = 'COMPLETED_SERVERS'
    BUILDING_ROUTES = 'BUILDING_ROUTES'
    COMPLETED_ROUTES = 'COMPLETED_ROUTES'
    BUILDING_FIREWALL = 'BUILDING_FIREWALL'
    COMPLETED_FIREWALL = 'COMPLETED_FIREWALL'
    BUILDING_STUDENT_ENTRY = 'BUILDING_STUDENT_ENTRY'
    COMPLETED_STUDENT_ENTRY = 'COMPLETED_STUDENT_ENTRY'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    STARTING = 'STARTING'
    READY = 'READY'
    EXPIRED = 'EXPIRED'
    MISFIT = 'MISFIT'
    BROKEN = 'BROKEN'
    BUILDING_ARENA_STUDENT_NETWORKS = 'BUILDING_ARENA_STUDENT_NETWORKS'
    COMPLETED_ARENA_STUDENT_NETWORKS = 'COMPLETED_ARENA_STUDENT_NETWORKS'
    BUILDING_ARENA_STUDENT_SERVERS = 'BUILDING_ARENA_STUDENT_SERVERS'
    COMPLETED_ARENA_STUDENT_SERVERS = 'COMPLETED_ARENA_STUDENT_SERVERS'
    BUILDING_ARENA_NETWORKS = 'BUILDING_ARENA_NETWORKS'
    COMPLETED_ARENA_NETWORKS = 'COMPLETED_ARENA_NETWORKS'
    BUILDING_ARENA_SERVERS = 'BUILDING_ARENA_SERVERS'
    COMPLETED_ARENA_SERVERS = 'COMPLETED_ARENA_SERVERS'
    GUACAMOLE_SERVER_LOAD_TIMEOUT = 'GUACAMOLE_SERVER_LOAD_TIMEOUT'
    NUKING = 'NUKING'
    READY_DELETE = 'READY_DELETE'
    DELETING_SERVERS = 'DELETING_SERVERS'
    COMPLETED_DELETING_SERVERS = 'COMPLETED_DELETING_SERVERS'
    DELETING_ARENA_FIREWALLS = 'DELETING_ARENA_FIREWALLS'
    COMPLETED_DELETING_ARENA_FIREWALLS = 'COMPLETED_DELETING_ARENA_FIREWALLS'
    DELETING_ARENA_ROUTES = 'DELETING_ARENA_ROUTES'
    COMPLETED_DELETING_ARENA_ROUTES = 'COMPLETED_DELETING_ARENA_ROUTES'
    DELETING_ARENA_SERVERS = 'DELETING_ARENA_SERVERS'
    COMPLETED_DELETING_ARENA_SERVERS = 'COMPLETED_DELETING_ARENA_SERVERS'
    DELETING_ARENA_SUBNETWORKS = 'DELETING_ARENA_SUBNETWORKS'
    COMPLETED_DELETING_ARENA_SUBNETWORKS = 'COMPLETED_DELETING_ARENA_SUBNETWORKS'
    DELETING_ARENA_NETWORKS = 'DELETING_ARENA_NETWORKS'
    COMPLETED_DELETING_ARENA_NETWORKS = 'DELETING_ARENA_NETWORKS'
    DELETED = 'DELETED'

ordered_workout_build_states = {
    BUILD_STATES.START: 0,
    BUILD_STATES.BUILDING_ASSESSMENT: 1,
    BUILD_STATES.BUILDING_NETWORKS: 2,
    BUILD_STATES.COMPLETED_NETWORKS: 3,
    BUILD_STATES.BUILDING_SERVERS: 4,
    BUILD_STATES.COMPLETED_SERVERS: 5,
    BUILD_STATES.BUILDING_ROUTES: 8,
    BUILD_STATES.COMPLETED_ROUTES: 9,
    BUILD_STATES.BUILDING_FIREWALL: 10
}


ordered_arena_states = {
    BUILD_STATES.START: 0,
    BUILD_STATES.BUILDING_ARENA_STUDENT_NETWORKS: 1,
    BUILD_STATES.COMPLETED_ARENA_STUDENT_NETWORKS: 2,
    BUILD_STATES.BUILDING_ARENA_STUDENT_SERVERS: 3,
    BUILD_STATES.COMPLETED_ARENA_STUDENT_SERVERS: 4,
    BUILD_STATES.BUILDING_ARENA_NETWORKS: 5,
    BUILD_STATES.COMPLETED_ARENA_NETWORKS: 6,
    BUILD_STATES.BUILDING_ARENA_SERVERS: 7,
    BUILD_STATES.COMPLETED_ARENA_SERVERS: 8,
    BUILD_STATES.BUILDING_ROUTES: 9,
    BUILD_STATES.COMPLETED_ROUTES: 10,
    BUILD_STATES.BUILDING_FIREWALL: 11,
    BUILD_STATES.COMPLETED_FIREWALL: 12,
    BUILD_STATES.DELETING_ARENA_FIREWALLS: 100,
    BUILD_STATES.COMPLETED_DELETING_ARENA_FIREWALLS: 101,
    BUILD_STATES.DELETING_ARENA_ROUTES: 102,
    BUILD_STATES.COMPLETED_DELETING_ARENA_ROUTES: 103,
    BUILD_STATES.DELETING_ARENA_SERVERS: 104,
    BUILD_STATES.COMPLETED_DELETING_ARENA_SERVERS: 105,
    BUILD_STATES.DELETING_ARENA_SUBNETWORKS: 106,
    BUILD_STATES.COMPLETED_DELETING_ARENA_SUBNETWORKS: 107,
    BUILD_STATES.DELETING_ARENA_NETWORKS: 108,
    BUILD_STATES.COMPLETED_DELETING_ARENA_NETWORKS: 109
}


class PUBSUB_TOPICS:
    MANAGE_SERVER = 'manage-server'
    DELETE_EXPIRED = 'maint-del-tmp-systems'



class SERVER_ACTIONS:
    BUILD = 'BUILD'
    START = 'START'
    DELETE = 'DELETE'
    STOP = 'STOP'
    REBUILD = 'REBUILD'
    SNAPSHOT = 'SNAPSHOT'
    RESTORE = 'RESTORE'


class WORKOUT_ACTIONS:
    BUILD = 'BUILD'
    NUKE = 'NUKE'


class BUILD_TYPES:
    MACHINE_IMAGE = 'machine-image'


class WORKOUT_TYPES:
    WORKOUT = "workout"
    ARENA = "arena"
    CONTAINER = "container"
    MISFIT = "misfit"


class ArenaWorkoutDeleteType:
    NETWORK = "network"
    SERVER = "server"
    FIREWALL_RULES = "firewall_rules"
    ROUTES = "routes"
    SUBNETWORK = "subnetwork"


class LOG_LEVELS:
    """
    GCP Logging API Severity Levels
    """
    DEBUG = 100
    INFO = 200
    NOTICE = 300
    WARNING = 400
    ERROR = 500
    CRITICAL = 600
    ALERT = 700
    EMERGENCY = 800


class LogIDs:
    ADMIN_SCRIPTS = 'admin-scripts'
    IOT = 'iot'
    SERVER_BUILD = "server-build"
    DELETION_MANAGEMENT = "deletion_management"
    BUDGET_MANAGEMENT = "budget_management"
    ATTACK_SCRIPTS = "attack-scripts"
    VULNERABILITY_SCRIPTS = "vulnerability-scripts"


class MAINTENANCE_ACTIONS:
    DELETE_EXPIRED = "delete_expired"
    STOP_LAPSED = "stop_lapsed"
    MEDIC = "medic"
    SNAPSHOT = "snapshot"


class AdminActions:
    CREATE_DNS_FORWARDING_FOR_UNIT = "create_dns_forwarding_for_unit"
    CREATE_NEW_SERVER_IN_UNIT = "create_new_server_in_unit"
    CREATE_NEW_WORKOUT_IN_UNIT = "create_new_workout_in_unit"
    CREATE_PRODUCTION_IMAGE = "create_production_image"
    DELETE_FULL_UNIT = "delete_full_unit"
    EXTEND_EXPIRATION_DAYS_UNIT = "extend_expiration_days_unit"
    FIX_SERVER_IN_UNIT = "fix_server_in_unit"
    FIX_STUDENT_ENTRY_IN_WORKOUT = "fix_student_entry_in_workout"
    NUKE_REBUILD_SERVER = "nuke_rebuild_server"
    NUKE_REBUILD_UNIT = "nuke_rebuild_unit"
    QUERY_WORKOUTS = "query_workouts"
    ADD_CHILD_PROJECT = "add_child_project"

class AdminInfoEntity:
    KIND = "cybergym-admin-info"
    class Entities:
        ADMINS = "admins"
        AUTHORIZED_USERS = "authorized_users"
        PENDING_USERS = "pending_users"
        CHILD_PROJECTS = "child_projects"


def test_server_existence(workout_id, server_name):
    try:
        server = compute.instances().get(project=project, zone=zone, instance=f"{workout_id}-{server_name}").execute()
    except HttpError:
        return False
    return True


def ds_safe_put(entity):
    """
    Stores a Datastore entity while excluding any indexing for fields longer than 1500 Bytes
    :param entity: A data store entity
    :return: None
    """
    exclude_from_indexes = []
    for item in entity:
        if type(entity[item]) == str and len(entity[item]) > 1500:
            exclude_from_indexes.append(item)
    entity.exclude_from_indexes = exclude_from_indexes
    try:
        ds_client.put(entity)
    except:
        print("Error storing entity")


def gcp_operation_wait(service, response, wait_type="zone", wait_seconds=150):
    """
    Wait for a gcp operation to complete
    :param service: The compute API connection object used for the operation
    :param response: The response object for the operation being waited on
    :param wait_type: The type of wait, either zone, region, or global. Defaults to zone
    :param wait_seconds: The number of seconds to wait before returning.
    :returns: True if the operation complete, and False if there is a timeout.
    """
    i = 0
    success = False
    max_wait_iteration = round(wait_seconds / 30)
    while not success and i < max_wait_iteration:
        try:
            print(f"Waiting for operation ID: {response['id']}")
            if wait_type == 'zone':
                response = service.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            elif wait_type == 'region':
                response = service.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()
            elif wait_type == 'global':
                service.globalOperations().wait(project=project, operation=response["id"]).execute()
            else:
                raise Exception("Unexpected wait_type in GCP operation wait function.")
            success = True
        except timeout:
            i += 1
            print(f"Response timeout for operation ID: {response['id']}. Trying again")
            pass
    if i >= max_wait_iteration:
        return False
    else:
        return True


def get_workout_type(workout):
    """
    Given a workout specifiction dictionary, this function returns the workout type.
    :param workout: A dictionary of a workout specification
    :returns: String, type of workout.
    """
    workout_type = None
    if 'build_type' not in workout:
        workout_type = WORKOUT_TYPES.WORKOUT
    else:
        workout_type = workout['build_type']
    return workout_type


def cloud_log(logging_id, message, severity=LOG_LEVELS.INFO):
    g_logger = log_client.logger(logging_id)
    g_logger.log_struct(
        {
            "message": message
        }, severity=severity
    )
