from google.cloud import datastore

ds_client = datastore.Client()
project = 'ualr-cybersecurity'


def set_workout_flag(workout_id):
    flag = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    ds_client.put(flag)
