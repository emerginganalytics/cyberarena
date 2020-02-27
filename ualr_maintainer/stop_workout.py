from globals import ds_client, project, compute, dnszone

# Global variables for this function
zone = 'us-central1-a'
region = 'us-central1'


def stop_workout(workout_id):
    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    if 'items' in result:
        for vm_instance in result['items']:
            response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()
        workout['running'] = False
        ds_client.put(workout)
    else:
        print("No workouts to stop")
