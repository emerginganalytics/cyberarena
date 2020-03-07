# Run this script to upload / update YAML files in the cloud bucket

from globals import storage_client, workout_globals
import os

# get bucket with name
bucket = storage_client.get_bucket(workout_globals.yaml_bucket)

yaml_directory = "../../yaml-files/"

def upload_yaml():
    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    for filename in os.listdir(yaml_directory):
        blob = bucket.get_blob(workout_globals.yaml_folder + filename)
        if blob == None:
            new_blob = bucket.blob(workout_globals.yaml_folder + filename)
            new_blob.upload_from_filename(yaml_directory + filename)
            print("Uploaded %s" % filename)
        else:
            if float(blob.updated.timestamp()) < os.path.getmtime(yaml_directory + filename):
                update_blob = bucket.blob(workout_globals.yaml_folder + filename)
                update_blob.upload_from_filename(yaml_directory + filename)
                print("Updated %s" % filename)
            else:
                print("%s is up to date" % filename)

upload_yaml()