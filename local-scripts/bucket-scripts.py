from utilities.globals import storage_client, workout_globals
from yaml import load, Loader

# get bucket with name
bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
# get bucket data as blob
blob = bucket.get_blob(workout_globals.yaml_folder + 'cs4360.yaml')
# convert to string
yaml_from_bucket = blob.download_as_string()
y = load(yaml_from_bucket, Loader=Loader)
a=1