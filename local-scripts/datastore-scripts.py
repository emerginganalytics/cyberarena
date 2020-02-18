from google.cloud import datastore
import calendar, time

ds_client = datastore.Client()

# store workout info to google cloud datastore
def store_workout_info(workout_id, user_mail, workout_duration, workout_type, timestamp, labentry_guac_path):
    # create a new user
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'labentry_guac_path': labentry_guac_path,
        'start_time': timestamp,
        'run_hours': 2,
        'timestamp': timestamp,
        'resources_deleted': False,
        'servers': []
    })

    # insert a new user
    ds_client.put(new_workout)


def add_workout_server_info(workout_id, server, ip_address):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["servers"].append({"server": server, "ip_address": ip_address})
    ds_client.put(workout)

def query_workouts():
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("resources_deleted", "=", False)
    for workout in list(query_workouts.fetch()):
        if not workout.key.name:
            key = workout.key
            workout_update = ds_client.get(key)
            workout_update["resources_deleted"] = True
            ds_client.put(workout_update)



def mark_old_workouts_deleted():
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("resources_deleted", "=", False)
    for workout in list(query_workouts.fetch()):
        if not workout.key.name:
            key = workout.key
            workout_update = ds_client.get(key)
            workout_update["resources_deleted"] = True
            ds_client.put(workout_update)


# store_workout_info('test', 'test@ualr.edu', 1, 'test-type', 23847927, 'tests')
# add_workout_server_info('test', 'my_server', "10.1.1.1")
mark_old_workouts_deleted()