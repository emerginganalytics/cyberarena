"""

"""
import calendar, time
from google.cloud import datastore, pubsub_v1
from common.state_transition import state_transition
from common.stop_compute import stop_workout
from common.globals import ds_client, BUILD_STATES, ordered_workout_build_states, WORKOUT_TYPES, get_workout_type, log_client, LOG_LEVELS, compute, SERVER_ACTIONS, PUBSUB_TOPICS, project, zone, cloud_log
from common.build_workout import build_workout
from common.nuke_workout import nuke_workout


def medic():
    """
    Reviews the state of all active workouts in the project and attempts to correct any which may have an invalid
    state. Invalid states often occur due to timeouts in processing the Google Cloud Functions.
    :returns: None
    """
    g_logger = log_client.logger('workout-actions')
    g_logger.log_text("MEDIC: Running Medic function")
    #
    # Fixing build timeout issues
    #
    # The add_filter does not have a != operator. This provides an equivalent results for active workouts.
    query_current_workouts = ds_client.query(kind='cybergym-workout')
    results = list(query_current_workouts.add_filter('active', '=', True).fetch())
    for workout in results:
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                if 'state' in workout:
                    build_state = workout['state']
                    # if the workout state has not completed, then attempt to continue rebuilding the workout from where
                    # it left off.
                    if build_state in ordered_workout_build_states:
                        g_logger.log_text("MEDIC: Workout {} is in a build state of {}. Attempting to fix...".format(workout.key.name, build_state))
                        build_workout(workout_id=workout.key.name)
                elif type(workout) is datastore.entity.Entity:
                    # If there is no state, then this is not a valid workout, and we can delete the Datastore entity.
                    g_logger.log_text("Invalid workout specification in the datastore for workout ID: {}. Deleting the record.".format(workout.key.name))
                    ds_client.delete(workout.key)
    #
    # Fixing workouts in state COMPLETED_FIREWALL. This may occur when the firewall gets built after the guacamole server
    #
    query_completed_firewalls = ds_client.query(kind='cybergym-workout')
    results = list(query_completed_firewalls.add_filter("state", "=", BUILD_STATES.COMPLETED_FIREWALL).fetch())
    for workout in results:
        # Only transition the state if the last state change occurred over 5 minutes ago.
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                if workout['state-timestamp'] < str(calendar.timegm(time.gmtime()) - 300):
                    g_logger.log_text("MEDIC: Workout {} stuck in firewall completion. Changing state to READY".format(workout.key.name))
                    state_transition(workout, new_state=BUILD_STATES.RUNNING)
                    stop_workout(workout.key.name)
    #
    # Fixing workouts in state GUACAMOLE_SERVER_TIMEOUT. This may occur waiting for the guacamole server to come up
    #
    query_student_entry_timeouts = ds_client.query(kind='cybergym-workout')
    results = list(query_student_entry_timeouts.add_filter("state", "=", BUILD_STATES.GUACAMOLE_SERVER_LOAD_TIMEOUT).
                   fetch())
    for workout in results:
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                # Change this to RUNNING unless the state change occurred over 15 minutes ago
                if workout['state-timestamp'] < str(calendar.timegm(time.gmtime()) - 900):
                    g_logger.log_text("MEDIC: Workout {} stuck in guacamole timeout. Changing state to READY".format(workout.key.name))
                    state_transition(workout, new_state=BUILD_STATES.RUNNING)
                    stop_workout(workout.key.name)
                else:
                    g_logger.log_text("MEDIC: Workout {} stuck in guacamole timeout. Changing state to READY".format(workout.key.name))
                    print(f"Workout {workout.key.name} stuck in guacamole timeout. Changing state to READY")
                    state_transition(workout, new_state=BUILD_STATES.READY)

    #
    # Fixing workouts in the state of STARTING. This may occur after a timeout in starting workouts.
    #
    query_start_timeouts = ds_client.query(kind='cybergym-workout')
    results = list(query_start_timeouts.add_filter("state", "=", BUILD_STATES.STARTING).fetch())
    for workout in results:
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                # Only transition the state if the last state change occurred over 5 minutes ago.
                if workout['state-timestamp'] < str(calendar.timegm(time.gmtime()) - 300):
                    g_logger.log_text("MEDIC: Workout {} stuck in a STARTING state. Stopping the workout.".format(workout.key.name))
                    state_transition(workout, new_state=BUILD_STATES.RUNNING)
                    stop_workout(workout.key.name)

    #
    # Fixing workouts in the state of STOPPING. This may occur after a timeout in stopping workouts.
    #
    query_stop_timeouts = ds_client.query(kind='cybergym-workout')
    results = list(query_stop_timeouts.add_filter("state", "=", BUILD_STATES.STOPPING).fetch())
    for workout in results:
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                # Only transition the state if the last state change occurred over 5 minutes ago.
                if workout['state-timestamp'] < str(calendar.timegm(time.gmtime()) - 300):
                    g_logger.log_text("MEDIC: Workout {} stuck in a STARTING state. Stopping the workout.".format(workout.key.name))
                    state_transition(workout, new_state=BUILD_STATES.RUNNING)
                    stop_workout(workout.key.name)

    #
    # Fixing workouts in the state of NUKING. This may occur after a timeout in deleting the workouts.
    #
    query_nuking_timeouts = ds_client.query(kind='cybergym-workout')
    results = list(query_nuking_timeouts.add_filter("state", "=", BUILD_STATES.NUKING).fetch())
    for workout in results:
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if get_workout_type(workout) == WORKOUT_TYPES.WORKOUT:
                # Only transition the state if the last state change occurred over 5 minutes ago.
                if workout['state-timestamp'] < str(calendar.timegm(time.gmtime()) - 300):
                    g_logger.log_text("MEDIC: Workout {} stuck in a NUKING state. Attempting to nuke again.".format(workout.key.name))
                    nuke_workout(workout.key.name)

    #
    #Fixing machines that did not get built
    #
    query_rebuild = ds_client.query(kind='cybergym-workout')
    query_rebuild.add_filter('state', '=', BUILD_STATES.READY)
    query_rebuild.add_filter('build_project_location', '=', project)
    running_machines = list(query_rebuild.fetch())
    current_machines = compute.instances().list(project=project, zone=zone).execute()

    list_current = []
    list_running = []
    list_missing = []

    current_machines_items = current_machines.get('items', None)
    while current_machines_items:
        for instance in current_machines_items:
            list_current.append(instance['name'])
        if 'nextPageToken' in current_machines:
            current_machines = compute.instances().list(project=project, zone=zone, pageToken=current_machines['nextPageToken']).execute()
            current_machines_items = current_machines.get('items', None)
        else:
            break
    for i in running_machines:
        unit = ds_client.get(ds_client.key('cybergym-unit', i['unit_id']))
        if unit['build_type'] == 'arena':
            for server in i['student_servers']:
                datastore_server_name = i.key.name+'-'+server['name']
                list_running.append(datastore_server_name)
                if datastore_server_name not in list_current:
                    list_missing.append(datastore_server_name)
        if unit['build_type'] == 'compute':
            for server in i['servers']:
                datastore_server_name = i.key.name+'-'+server['name']
                list_running.append(datastore_server_name)
                if datastore_server_name not in list_current:
                    list_missing.append(datastore_server_name)

    cloud_log('Medic', f'Missing servers{list_missing}', LOG_LEVELS.INFO)
    
    for server in list_missing:
        cloud_log('Medic', 'Rebuilding server{}'.format(server), LOG_LEVELS.INFO)
        pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        future = publisher.publish(topic_path, data=b'Server Build', server_name=server, action=SERVER_ACTIONS.BUILD)       


    return
