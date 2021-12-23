import time, calendar
from google.cloud import pubsub_v1
from common.globals import ds_client, log_client, project, compute, BUILD_STATES, PUBSUB_TOPICS, SERVER_ACTIONS, LOG_LEVELS
from common.state_transition import state_transition

# Global variables for this function
zone = 'us-central1-a'
region = 'us-central1'


def stop_workout(workout_id):
    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.READY, existing_state=BUILD_STATES.RUNNING)
    start_time = None
    if 'start_time' in workout:
        start_time = workout['start_time']
        stop_time = calendar.timegm(time.gmtime())
        runtime = int(stop_time) - int(start_time)
        if 'runtime_counter' in workout:
            accumulator = workout['runtime_counter']
            new_runtime = int(accumulator) + runtime
            workout['runtime_counter'] = new_runtime
        else:
            workout['runtime_counter'] = runtime
    ds_client.put(workout)
    query_workout_servers = ds_client.query(kind='cybergym-server')
    query_workout_servers.add_filter("workout", "=", workout_id)
    for server in list(query_workout_servers.fetch()):
        # Publish to a server management topic
        pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        future = publisher.publish(topic_path, data=b'Server Build', server_name=server['name'],
                                   action=SERVER_ACTIONS.STOP)
        print(future.result())
    g_logger = log_client.logger(str(workout_id))
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()
        g_logger.log_struct(
            {
                "message": "Workout stopped"
            }, severity=LOG_LEVELS.INFO
        )
    else:
        g_logger.log_struct(
            {
                "message": "No workouts to stop"
            }, severity=LOG_LEVELS.WARNING
        )


def stop_everything():
    g_logger = log_client.logger('workout-actions')
    result = compute.instances().list(project=project, zone=zone).execute()
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()
        g_logger.log_struct(
            {
                "message": "All machines stopped (daily cleanup)",
            }, severity=LOG_LEVELS.INFO
        )
    else:
        g_logger.log_struct(
            {
                "message": "No workouts to stop (daily cleanup)"
            }, severity=LOG_LEVELS.WARNING
        )


def stop_arena(unit_id):
    """
    Arenas have server builds for the unit as well as individual workouts. This function
    stops all of these servers
    :param unit_id: The build ID of the arena
    :return: None
    """
    # First stop the unit's servers
    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(unit_id)).execute()
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    unit['arena']['running'] = False
    ds_client.put(unit)
    g_logger = log_client.logger('arena-actions')
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()
        g_logger.log_struct(
            {
                "message": "Stopped servers for arena {}".format(unit_id)
            }, severity=LOG_LEVELS
        )
    else:
        g_logger.log_struct(
            {
                "message": "No servers in arena {} to stop".format(unit_id)
            }, severity=LOG_LEVELS.WARNING
        )

    for workout_id in unit['workouts']:
        g_logger = log_client.logger(str(workout_id))
        result = compute.instances().list(project=project, zone=zone,
                                          filter='name = {}*'.format(workout_id)).execute()
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        workout['running'] = False
        ds_client.put(workout)
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().stop(project=project, zone=zone,
                                                    instance=vm_instance["name"]).execute()
            g_logger.log_struct(
                {
                    "message": "Workout servers stopped for workout {}".format(workout_id)
                }, severity=LOG_LEVELS.INFO
            )
            
        else:
            g_logger.log_struct(
                {
                    "message": "No servers to stop for workout {}".format(workout_id)
                }, severity=LOG_LEVELS.WARNING
            )


def stop_lapsed_workouts():
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("state", "=", BUILD_STATES.RUNNING)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if "start_time" in workout and "run_hours" in workout and workout.get('type', 'arena') != 'arena':
                workout_id = workout.key.name
                start_time = int(workout.get('start_time', 0))
                run_hours = int(workout.get('run_hours', 0))

                # Stop the workout servers if the run time has exceeded the request
                if ts - start_time >= run_hours * 3600:
                    g_logger = log_client.logger(str(workout_id))
                    g_logger.log_struct(
                        {
                            "message": "The workout {} has exceeded its run time and will be stopped".format(workout_id)
                        }, severity=LOG_LEVELS.INFO
                    )
                    stop_workout(workout_id)


def stop_lapsed_arenas():
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_units = ds_client.query(kind='cybergym-unit')
    query_units.add_filter("arena.running", "=", True)
    for unit in list(query_units.fetch()):
        if 'arena' in unit and "gm_start_time" in unit['arena'] and "run_hours" in unit['arena']:
            unit_id = unit.key.name
            start_time = int(unit['arena'].get('gm_start_time', 0))
            run_hours = int(unit['arena'].get('run_hours', 0))

            # Stop the workout servers if the run time has exceeded the request
            if ts - start_time >= run_hours * 3600:
                g_logger = log_client.logger('arena-actions')
                g_logger.log_struct(
                    {
                        "message": "The arena {} has exceeded its run time and will be stopped".format(unit_id)
                    }, severity=LOG_LEVELS.INFO
                )
                stop_arena(unit_id)
