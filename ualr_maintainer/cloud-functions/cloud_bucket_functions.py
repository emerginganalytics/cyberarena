from globals import storage_client, workout_globals
from yaml import load, Loader
import os

# get bucket with name
bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
# get bucket data as blob
blob = bucket.get_blob(workout_globals.yaml_folder + 'cs4360.yaml')
# convert to string
yaml_from_bucket = blob.download_as_string()
y = load(yaml_from_bucket, Loader=Loader)
a=1

def upload_yaml(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
