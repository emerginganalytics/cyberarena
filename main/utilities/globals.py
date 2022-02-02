import googleapiclient.discovery
import logging
from google.cloud import datastore, runtimeconfig, storage
from google.cloud import logging as g_logging


runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
region = myconfig.get_variable('region').value.decode("utf-8")
zone = myconfig.get_variable('zone').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
script_repository = myconfig.get_variable('script_repository').value.decode("utf-8")
api_key = myconfig.get_variable('api_key').value.decode("utf-8")
custom_dnszone = myconfig.get_variable('dnszone')
student_instructions_url = myconfig.get_variable('student_instructions_url')
student_instructions_url = student_instructions_url.value.decode("utf-8") if student_instructions_url else \
    'https://storage.googleapis.com/student_workout_instructions_ualr-cybersecurity/'
teacher_instructions_url = myconfig.get_variable('teacher_instructions_url')
teacher_instructions_url = teacher_instructions_url.value.decode("utf-8") if teacher_instructions_url else \
    'https://storage.googleapis.com/teacher_workout_instructions_ualr-cybersecurity/'
if custom_dnszone != None:
    dnszone = custom_dnszone.value.decode("utf-8")
else:
    dnszone = 'cybergym-public'
main_app_url = myconfig.get_variable('main_app_url').value.decode("utf-8")
guac_db_password = myconfig.get_variable('guac_password')
guac_db_password = guac_db_password.value.decode("utf-8")

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
log_client = g_logging.Client()

workout_token = 'RG987S1GVNKYRYHYA'

auth_config = {
    'api_key': api_key,
    'auth_domain': str(project + ".firebaseapp.com"),
    'project_id': project
}

# Use this for debugging. Uncomment the above endpoint for final environment.
post_endpoint = 'http://localhost:8080/complete'
logger = logging.getLogger()


class workout_globals():
    MAX_RUN_HOURS = 10
    yaml_bucket = project + '_cloudbuild'
    yaml_folder = 'yaml-build-files/'
    windows_startup_script_env = 'setx /m WORKOUTID {env_workoutid}\n' \
                                 'setx /m URL ' + main_app_url + '\n' \
                                                                 'setx /m DNS_SUFFIX ' + dns_suffix + '\n'
    windows_startup_script_task = 'setx /m WORKOUTKEY{q_number} {env_workoutkey}\n' \
                                  'call gsutil cp ' + script_repository + '{script} .\n' \
                                                                          'schtasks /Create /SC MINUTE /TN {script_name} /RU System /TR {script_command}'
    linux_startup_script_env = '#! /bin/bash\n' \
                               'cat >> /etc/environment << EOF\n' \
                               'WORKOUTID={env_workoutid}\n' \
                               'URL=' + main_app_url + '\n' \
                                                       'DNS_SUFFIX=' + dns_suffix + '\n'
    linux_startup_script_task = 'cat >> /etc/environment << EOF\n' \
                                'WORKOUTKEY{q_number}={env_workoutkey}\n' \
                                'EOF\n' \
                                'gsutil cp ' + script_repository + '{script} {local_storage}\n' \
                                                                   '(crontab -l 2>/dev/null; echo "* * * * * {script_command}") | crontab -'
    max_workout_len = 100
    max_num_workouts = 200
    ps_build_workout_topic = 'build-workouts'
    ps_build_arena_topic = 'build_arena'
    student_instruction_folder = "student_workout_instructions_" + project
    teacher_instruction_folder = "teacher_workout_instructions_" + project

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
            logger.error("Timeout for operation %s" % operation_id)
            return False
        else:
            return True

    @staticmethod
    def refresh_api():
        compute = googleapiclient.discovery.build('compute', 'v1')
        return compute


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
    DELETING_SERVERS = 'DELETING_SERVERS'
    COMPLETED_DELETING_SERVERS = 'COMPLETED_DELETING_SERVERS'
    DELETED = 'DELETED'


class LogIDs:
    MAIN_APP = 'cyberarena-app'
    USER_AUTHORIZATION = 'cyberarena-login'

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


def cloud_log(logging_id, message, severity):
    """
    Global function to log messages to cloud project.
    @param logging_id: The facility to log under
    @param message: Logging message
    @param severity: LOG_LEVELS
    @type severity: Integer
    @return: None
    """
    g_logger = log_client.logger(logging_id)
    g_logger.log_struct(
        {
            "message": message
        }, severity=severity
    )


class AdminInfoEntity:
    KIND = "cybergym-admin-info"
    class Entities:
        ADMINS = "admins"
        AUTHORIZED_USERS = "authorized_users"
        PENDING_USERS = "pending_users"
        CHILD_PROJECTS = "child_projects"


class AdminActions:
    CREATE_DNS_FORWARDING_FOR_UNIT = {
        "function_name": "create_dns_forwarding_for_unit", 
        "params": ["ip_address", "network"]
        } 
    CREATE_NEW_SERVER_IN_UNIT = {
        "function_name": "create_new_server_in_unit",
        "params": ["build_id", "build_server_spec"]
        }
    CREATE_PRODUCTION_IMAGE = {
        "function_name": "create_production_image",
        "params": ["server_name"]
        }
    DELETE_FULL_UNIT = {
        "function_name": "delete_full_unit",
        "params": ["unit_id"]
        }
    EXTEND_EXPIRATION_DAYS_UNIT = {
        "function_name":"extend_expiration_days_unit",
        "params": ["unit_id", "expiration"]
        }
    FIX_SERVER_IN_UNIT = {
        "function_name": "fix_server_in_unit",
        "params": ["build_id", "server_name", "type", "parameters"]
        }
    NUKE_REBUILD_SERVER = {
        "function_name": "nuke_rebuild_server",
        "params": ["server_name"]
        }
    NUKE_REBUILD_UNIT = {
        "function_name": "nuke_rebuild_unit",
        "params": ["unit_id"]
        }
    QUERY_WORKOUTS = {
        "function_name": "query_workouts",
        "params": ["query_type"]
        }
    ADD_CHILD_PROJECT = {
        "function_name": "add_child_project",
        "params": ["child_project"]
        }


class BuildTypes:
    COMPUTE = "compute"
    ARENA = "arena"
    CONTAINER = "container"
    Types = [COMPUTE, ARENA, CONTAINER]


class ComputeBuildTypes:
    MACHINE_IMAGE = 'machine-image'
