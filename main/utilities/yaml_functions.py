from utilities.globals import storage_client, workout_globals, cloud_log, LOG_LEVELS, LogIDs
import yaml
from os import remove, path


class YamlFunctions(object):
    def __init__(self):
        self.bucket = storage_client.get_bucket(workout_globals.yaml_bucket)

    def parse_yaml(self, yaml_filename):
        """
        Pull and validate yaml contents from a designated project cloud bucket
        :param yaml_filename: Both the workout type and filename of the yaml file in the cloud bucket
        :return: The yaml string from the cloud bucket
        """
        blob = self.bucket.get_blob(workout_globals.yaml_folder + yaml_filename + ".yaml")
        if not blob:
            cloud_log(LogIDs.MAIN_APP, f"YAML file not found: {yaml_filename}", LOG_LEVELS.ERROR)
            raise FileNotFoundError
        yaml_string = blob.download_as_string()
        try:
            y = yaml.safe_load(yaml_string)
        except yaml.YAMLError as err:
            cloud_log(LogIDs.MAIN_APP, f"Error parsing specified yaml file: {yaml_filename}", LOG_LEVELS.ERROR)
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                cloud_log(LogIDs.MAIN_APP, f"Error position: ({mark.line + 1}:{mark.column + 1})", LOG_LEVELS.ERROR)
            raise
        return y

    def generate_yaml_content(self, json_data):
        yaml_info = {}
        yaml_info['content_list'] = []

        with open('temp.yaml', 'w') as temp:
            test = yaml.dump(json_data, temp)
            temp.close()
        with open('temp.yaml', 'r') as temp:
            for line in temp.readlines():
                yaml_info['content_list'].append(line)
            temp.close()
        if (path.exists('temp.yaml')):
            remove('temp.yaml')

        return yaml_info

    def save_yaml_file(self, json_data):
        workout_name = json_data['workout']['name']
        workout_name.replace(" ", "")
        workout_name = workout_name.lower()
        workout_name += ".yaml"
        with open(workout_name, 'w') as temp:
            test = yaml.dump(json_data, temp)
            temp.close()

        new_blob = self.bucket.blob(workout_globals.yaml_folder + workout_name)
        with open(workout_name, 'rb') as temp:
            new_blob.upload_from_file(temp, content_type='application/octet-stream')

            temp.close()
        if (path.exists(workout_name)):
            remove(workout_name)
        return True


def parse_workout_yaml(yaml_filename):
    """
    Pull and validate yaml contents from a designated project cloud bucket
    :param yaml_filename: Both the work type and filename of the yaml file in the cloud bucket
    :return: The yaml string from the cloud bucket
    """
    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    blob = bucket.get_blob(workout_globals.yaml_folder + yaml_filename + ".yaml")
    if not blob:
        cloud_log(LogIDs.MAIN_APP, f"YAML file not found: {yaml_filename}", LOG_LEVELS.ERROR)
        raise FileNotFoundError
    yaml_string = blob.download_as_string()
    try:
        y = yaml.safe_load(yaml_string)
    except yaml.YAMLError as err:
        cloud_log(LogIDs.MAIN_APP, f"Error parsing specified yaml file: {yaml_filename}", LOG_LEVELS.ERROR)
        if hasattr(err, 'problem_mark'):
            mark = err.problem_mark
            cloud_log(LogIDs.MAIN_APP, f"Error position: ({mark.line + 1}:{mark.column + 1})", LOG_LEVELS.ERROR)
        raise
    return y


def generate_yaml_content(json_data):
    yaml_info = {}
    yaml_info['content_list'] = []

    with open('temp.yaml', 'w') as temp:
        test = yaml.dump(json_data, temp)
        temp.close()
    with open('temp.yaml', 'r') as temp:
        for line in temp.readlines():
            yaml_info['content_list'].append(line)
        temp.close()
    if (path.exists('temp.yaml')):
        remove('temp.yaml')

    return yaml_info


def save_yaml_file(json_data):
    workout_name = json_data['workout']['name']
    workout_name.replace(" ", "")
    workout_name = workout_name.lower()
    workout_name += ".yaml"
    with open(workout_name, 'w') as temp:
        test = yaml.dump(json_data, temp)
        temp.close()

    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    new_blob = bucket.blob(workout_globals.yaml_folder + workout_name)
    with open(workout_name, 'rb') as temp:
        new_blob.upload_from_file(temp, content_type='application/octet-stream')

        temp.close()
    if (path.exists(workout_name)):
        remove(workout_name)

    return True

