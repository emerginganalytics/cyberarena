import base64
import json
import sys
from json.decoder import JSONDecodeError
from admin_scripts.add_child_project import add_child_project
from admin_scripts.create_dns_forwarding_for_unit import create_dns_forwarding
from common.build_competition_arena import CompetitionArena
from common.build_workout import build_workout
from common.compute_management import server_build, server_start, server_delete, server_stop, Snapshot
from common.database.iot_database import IOTDatabase
from common.database.nvd_update import nvd_update
from common.delete_expired_workouts import DeletionManager
from common.globals import AdminActions, ArenaWorkoutDeleteType, cloud_log, LogIDs, log_client,  LOG_LEVELS, \
    MAINTENANCE_ACTIONS, project, SERVER_ACTIONS, WORKOUT_ACTIONS, WORKOUT_TYPES
from common.medic import medic
from common.database.iot_database import IOTDatabase
from common.budget_management import BudgetManager
from common.nuke_workout import nuke_workout
from common.start_vm import start_vm, start_arena
from common.stop_compute import stop_workout, stop_lapsed_workouts, stop_lapsed_arenas, stop_everything
from common.publish_compute_image import create_production_image
from admin_scripts.create_dns_forwarding_for_unit import create_dns_forwarding
from admin_scripts.add_child_project import add_child_project
from admin_scripts.delete_full_unit import delete_unit
from admin_scripts.nuke_rebuild_server import nuke_rebuild_server
from admin_scripts.nuke_rebuild_unit import nuke_rebuild_unit
from admin_scripts.fix_student_entry_in_workout import fix_student_entry_in_workout
from admin_scripts.create_new_workout_in_unit import create_new_workout_in_unit
from admin_scripts.create_new_server_in_unit import create_new_server_in_unit


bm = BudgetManager()


def cloud_fn_build_workout(event, context):
    """ Responds to a pub/sub event in which the user has included
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_build_workout because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None
    action = event['attributes']['action'] if 'action' in event['attributes'] else None

    if not workout_id:
        print(f'No workout ID provided in cloud_fn_build_workout for published message')
        return

    g_logger = log_client.logger(workout_id)
    if action == WORKOUT_ACTIONS.NUKE:
        g_logger.log_text(f"Nuking and rebuilding workout")
        nuke_workout(workout_id)
    else:
        g_logger.log_text(f"Building workout")
        build_workout(workout_id)

    if context:
        g_logger.log_text(f"Workout action has completed.")


def cloud_fn_build_arena(event, context):
    """ Responds to a pub/sub event in which the user has included
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_build_arena because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    unit_id = event['attributes']['unit_id'] if 'unit_id' in event['attributes'] else None
    CompetitionArena(unit_id).build()

    if context:
        print("Workout %s has completed." % unit_id)


def cloud_fn_start_vm(event, context):
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_start_vm because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_vm(workout_id)


def cloud_fn_stop_vm(event, context):
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_stop_vm because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False
    
    stop_workout(workout_id)


def cloud_fn_start_arena(event, context):
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_start_arena because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    unit_id = event['attributes']['unit_id'] if 'unit_id' in event['attributes'] else None

    if not unit_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_arena(unit_id)


def cloud_fn_delete_expired_workout(event, context):
    """
    Cloud function calls a local function to delete all expired and misfit workouts in the project.
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_delete_expired_workout because the "
                                            "budget exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    build_type = event['attributes'].get('workout_type', WORKOUT_TYPES.WORKOUT)
    workout_id = event['attributes'].get('workout_id', None)
    unit_id = event['attributes'].get('unit_id', None)
    arena_workout_delete_type = event['attributes'].get('arena_workout_delete_type', None)

    build_id = None
    if build_type == WORKOUT_TYPES.WORKOUT:
        if workout_id:
            deletion_type = DeletionManager.DeletionType.SPECIFIC
            build_id = workout_id
        else:
            deletion_type = DeletionManager.DeletionType.EXPIRED
    elif build_type == WORKOUT_TYPES.ARENA:
        if unit_id:
            deletion_type = DeletionManager.DeletionType.SPECIFIC
            build_id = unit_id
        elif workout_id:    # If a workout is specified with arena build, then there is a component to delete.
            deletion_type = arena_workout_delete_type
            build_id = workout_id
        else:
            deletion_type = DeletionManager.DeletionType.EXPIRED
    elif build_type == WORKOUT_TYPES.MISFIT:
        deletion_type = DeletionManager.DeletionType.MISFIT
    else:
        cloud_log(LogIDs.DELETION_MANAGEMENT, f"Unsupported workout type sent to delete function: {build_type}",
                  LOG_LEVELS.ERROR)
        return False
    cloud_log(LogIDs.DELETION_MANAGEMENT, f"Running job for deletion type: {deletion_type}, build id: {build_id}, "
                                          f"and build type: {build_type}", LOG_LEVELS.INFO)
    dm = DeletionManager(deletion_type=deletion_type, build_id=build_id, build_type=build_type)
    dm.run()


def cloud_fn_stop_lapsed_workouts(event, context):
    """
    Stops expired workouts based on the current time and the number of hours specified to run in the datastore
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_stop_lapsed_workouts because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return
    stop_lapsed_workouts()


def cloud_fn_stop_lapsed_arenas(event, context):
    """
    Stops expired arenas based on the current time and the number of hours specified to run in the datastore
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_stop_lapsed_arenas because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    stop_lapsed_arenas()


def cloud_fn_manage_server(event, context):
    """ Responds to a pub/sub event from other cloud functions to build servers.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_manage_server because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    server_name = event['attributes']['server_name'] if 'server_name' in event['attributes'] else None
    action = event['attributes']['action'] if 'action' in event['attributes'] else None

    if not server_name:
        print(f'No server name provided in cloud_fn_manage_server for published message')
        return

    if not action:
        print(f'No action provided in cloud_fn_manage_server for published message.')
        return

    if action == SERVER_ACTIONS.BUILD:
        server_build(server_name)
    elif action == SERVER_ACTIONS.START:
        server_start(server_name)
    elif action == SERVER_ACTIONS.DELETE:
        server_delete(server_name)
    elif action == SERVER_ACTIONS.STOP:
        server_stop(server_name)
    elif action == SERVER_ACTIONS.SNAPSHOT:
        Snapshot.snapshot_server(server_name)
    elif action == SERVER_ACTIONS.RESTORE:
        Snapshot.restore_server(server_name)


def cloud_fn_medic(event, context):
    """
    Cloud function to fix all misfit workouts which are mostly due to timeouts in the cloud function when building
    and managing workouts..
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_medic because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    medic()


def cloud_fn_daily_maintenance(event, context):
    """
    Performs regular maintenance for all systems in the cloud project.
    This will eventually move all cloud maintenance to a single function to require fewer number and updates for
    cloud functions.
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_daily_maintenance because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    stop_everything()
    Snapshot.snapshot_all()
    nvd_update()


def cloud_fn_admin_scripts(event, context):
    """
    Provides access to backend maintenance scripts to perform a variety of different tasks
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_admin_scripts because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return

    script_info = json.loads(event['attributes'].get('script_dict'))
    action = Utilities.check_variable(script_info, 'function_name', 'test', LogIDs.ADMIN_SCRIPTS)
    params = Utilities.check_variable(script_info, 'params', 'test', LogIDs.ADMIN_SCRIPTS)
    cloud_log(LogIDs.ADMIN_SCRIPTS, message=f"{action}\n{params}", severity=LOG_LEVELS.INFO)
    # build_id = event['attributes'].get('build_id', None)
    if action == AdminActions.CREATE_DNS_FORWARDING_FOR_UNIT:
        build_id = Utilities.check_variable(params, 'build_id', AdminActions.CREATE_DNS_FORWARDING_FOR_UNIT, LogIDs.ADMIN_SCRIPTS)
        ip_address = Utilities.check_variable(params, 'ip_address', AdminActions.CREATE_DNS_FORWARDING_FOR_UNIT, build_id)
        network = Utilities.check_variable(params, 'network', AdminActions.CREATE_DNS_FORWARDING_FOR_UNIT, build_id)
        create_dns_forwarding(build_id, ip_address, network)

    elif action == AdminActions.ADD_CHILD_PROJECT:
        child_project = Utilities.check_variable(params, 'child_project', AdminActions.ADD_CHILD_PROJECT, project)
        add_child_project(child_project)

    elif action == AdminActions.CREATE_PRODUCTION_IMAGE:
        server_name = Utilities.check_variable(params, 'server_name', AdminActions.CREATE_PRODUCTION_IMAGE, project)
        create_production_image(server_name)
        
    elif action == AdminActions.DELETE_FULL_UNIT:
        unit_id = Utilities.check_variable(params, 'unit_id', AdminActions.DELETE_FULL_UNIT, project)
        delete_unit(unit_id)

    elif action == AdminActions.NUKE_REBUILD_SERVER:
        server_name = Utilities.check_variable(params, 'server_name', AdminActions.NUKE_REBUILD_SERVER, LogIDs.ADMIN_SCRIPTS)
        cloud_log(LogIDs.ADMIN_SCRIPTS, message=f"Nuking and Rebuilding {server_name}", severity=LOG_LEVELS.INFO)
        nuke_rebuild_server(server_name)

    elif action == AdminActions.NUKE_REBUILD_UNIT:
        unit_id = Utilities.check_variable(params, 'unit_id', AdminActions.NUKE_REBUILD_UNIT, LogIDs.ADMIN_SCRIPTS)
        nuke_rebuild_unit(unit_id)

    elif action == AdminActions.FIX_STUDENT_ENTRY_IN_WORKOUT:
        workout_id = Utilities.check_variable(params, 'workout_id', AdminActions.FIX_STUDENT_ENTRY_IN_WORKOUT, LogIDs.ADMIN_SCRIPTS)
        fix_student_entry_in_workout(workout_id)

    elif action == AdminActions.CREATE_NEW_WORKOUT_IN_UNIT:
        unit_id = Utilities.check_variable(params, 'unit_id', AdminActions.CREATE_NEW_WORKOUT_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        student_name = Utilities.check_variable(params, 'student_name', AdminActions.CREATE_NEW_WORKOUT_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        email_address = Utilities.check_variable(params, 'email_address', AdminActions.CREATE_NEW_WORKOUT_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        registration_required = Utilities.check_variable(params, 'registration_required', AdminActions.CREATE_NEW_WORKOUT_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        create_new_workout_in_unit(unit_id, student_name, email_address, registration_required)

    elif action == AdminActions.CREATE_NEW_SERVER_IN_UNIT:
        unit_id = Utilities.check_variable(params, 'unit_id', AdminActions.CREATE_NEW_SERVER_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        build_server_spec = Utilities.check_variable(params, 'build_server_spec', AdminActions.CREATE_NEW_SERVER_IN_UNIT, LogIDs.ADMIN_SCRIPTS)
        create_new_server_in_unit(unit_id, build_server_spec)


def cloud_fn_iot_capture_sensor(event, context):
    """
        Listens on IOT PubSub topic and updates and forwards data from a SQL database to the Classified Cloud Run
        application.
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_iot_capture_sensor because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return
    my_function_name = "cloud_fn_iot_capture_sensor"
    device_num_id = Utilities.check_variable(event['attributes'], 'deviceNumId', my_function_name, LogIDs.IOT)
    sensor_data = Utilities.check_variable(event, 'data', my_function_name, LogIDs.IOT)
    event_data = json.loads(base64.b64decode(sensor_data).decode('UTF-8'))

    system_data = event_data.get('system', None)
    memory = ip = storage = None

    print(event)
    print(f'telemetry data: {event_data}')
    if system_data:
        memory = system_data.get('memory', None)
        ip = system_data.get('ip', None)
        storage = system_data.get('storage', None)

    iotdb = IOTDatabase()
    try:
        iotdb.update_rpi_sense_hat_data(device_num_id=device_num_id,
                                        ts=event_data['ts'],
                                        sensor_data=json.dumps(event_data['sensor_data']),
                                        memory=memory,
                                        ip=ip,
                                        storage=storage)
    except KeyError as err:
        cloud_log(LogIDs.IOT, f"Key error: '{err.args[0]}' not found", LOG_LEVELS.ERROR)
    except:
        cloud_log(LogIDs.IOT, f"Unspecified error when updating IoT", LOG_LEVELS.ERROR)


def cloud_fn_budget_manager(event, context):
    """
    Handles budget events for the project. If the budget hits 100%, then a global variable will be set so such that
    cloud functions will not respond.
    """
    try:
        pubsub_json = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    except KeyError:
        cloud_log(LogIDs.BUDGET_MANAGEMENT, f"Budget PubSub message has no data key!", LOG_LEVELS.ERROR)
        return
    except JSONDecodeError:
        cloud_log(LogIDs.BUDGET_MANAGEMENT, f"Error decoding budget notification. Received data: {event['data']}",
                  LOG_LEVELS.ERROR)
        return

    cost_amount = pubsub_json['costAmount']
    budget_amount = pubsub_json['budgetAmount']

    cloud_log(LogIDs.BUDGET_MANAGEMENT, f"Budget Management function triggered with current cost as "
                                        f"${cost_amount} against the budget ${budget_amount}.")

    if cost_amount >= budget_amount:
        bm.set_budget_exceeded()


class Utilities:
    @staticmethod
    def check_variable(attributes, var_name, function_name, log_id):
        return_var = attributes.get(var_name, None)
        if not return_var:
            cloud_log(log_id, f"In admin script {function_name}"
                              f", did not supply ip_address parameter! System exiting.", LOG_LEVELS.ERROR)
            sys.exit()
        return return_var
