import time, calendar

from common.globals import ds_client, project, compute

# Global variables for this function
zone = 'us-central1-a'
region = 'us-central1'


def stop_workout(workout_id):
    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    workout['running'] = False
    ds_client.put(workout)
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()

        print("Workouts stopped")
    else:
        print("No workouts to stop")


def stop_everything():
    result = compute.instances().list(project=project, zone=zone).execute()
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()

        print("Workouts stopped")
    else:
        print("No workouts to stop")


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
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()

        print("Unit servers stopped")
    else:
        print("No unit servers to stop")

    for workout_id in unit['workouts']:
        result = compute.instances().list(project=project, zone=zone,
                                          filter='name = {}*'.format(workout_id)).execute()
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        workout['running'] = False
        ds_client.put(workout)
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().stop(project=project, zone=zone,
                                                    instance=vm_instance["name"]).execute()

            print("Workout servers stopped for %s" % workout_id)
        else:
            print("No workout servers to stop for %s" % workout_id)


def stop_lapsed_workouts():
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("running", "=", True)
    for workout in list(query_workouts.fetch()):
        if "start_time" in workout and "run_hours" in workout and workout.get('type', 'arena') != 'arena':
            workout_id = workout.key.name
            start_time = int(workout.get('start_time', 0))
            run_hours = int(workout.get('run_hours', 0))

            # Stop the workout servers if the run time has exceeded the request
            if ts - start_time >= run_hours * 3600:
                stop_workout(workout_id)


def stop_lapsed_arenas():
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_units = ds_client.query(kind='cybergym-unit')
    query_units.add_filter("arena.running", "=", True)
    for unit in list(query_units.fetch()):
        if 'arena' in unit and "start_time" in unit['arena'] and "run_hours" in unit['arena']:
            unit_id = unit.key.name
            start_time = int(unit['arena'].get('start_time', 0))
            run_hours = int(unit['arena'].get('run_hours', 0))

            # Stop the workout servers if the run time has exceeded the request
            if ts - start_time >= run_hours * 3600:
                stop_arena(unit_id)

# stop_lapsed_arenas()