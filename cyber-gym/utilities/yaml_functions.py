from utilities.globals import storage_client, workout_globals


def parse_workout_yaml(workout_type):
    """
    Pull and validate yaml contents from a designated project cloud bucket
    :param workout_type: Both the work type and filename of the yaml file in the cloud bucket
    :return: The yaml string from the cloud bucket
    """
    # Open and read YAML file
    print('Loading config file')
    # get bucket with name
    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    blob = bucket.get_blob(workout_globals.yaml_folder + workout_type + ".yaml")
    if not blob:
        return False
    # convert to string
    yaml_string = blob.download_as_string()
    return yaml_string
