from google.cloud import datastore
from globals import ds_client, logger

# Store information for an instructor. To be used when instructor login is complete
def store_instructor_info(email):
    new_instructor = datastore.Entity(ds_client.key('cybergym-instructor', email))

    new_instructor.update({
        "units": []
    })

    ds_client.put(new_instructor)

# Store information for an individual unit.
def store_unit_info(id, email, name, ts, workout_type, student_instructions_url, workout_description):

    new_unit = datastore.Entity(ds_client.key('cybergym-unit', id))

    new_unit.update({
        "name": name,
        "instructor_id": email,
        "timestamp": ts,
        "workout_type": workout_type,
        "description": workout_description,
        "student_instructions_url": student_instructions_url,
        "workouts": [],
        "ready": False
    })

    ds_client.put(new_unit)

# This function queries and returns all workout IDs for a given unit
def get_unit_workouts(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):
        workout_instance = workout = ds_client.get(workout.key)
        workout_info = {
            'name': workout.key.name,
            'running': workout_instance['running']
        }
        workout_list.append(workout_info)

    return workout_list

# store workout info to google cloud datastore
def store_workout_info(workout_id, unit_id, user_mail, workout_duration, workout_type, timestamp):
    # create a new user
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'start_time': timestamp,
        'run_hours': 0,
        'timestamp': timestamp,
        'resources_deleted': False,
        'running': False,
        'servers': [],
        'complete': False
    })

    # insert a new user
    ds_client.put(new_workout)


def print_workout_info(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    for server in workout["servers"]:
        if server["server"] == workout_id + "-cybergym-labentry":
            print("%s: http://%s:8080/guacamole/#/client/%s" %(workout_id, server["ip_address"],
                                                               workout['labentry_guac_path']))