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
