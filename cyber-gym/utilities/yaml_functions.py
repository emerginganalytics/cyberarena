from utilities.globals import storage_client, workout_globals
import yaml
from os import remove, path

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
    if(path.exists('temp.yaml')):
        remove('temp.yaml')

    return yaml_info

def save_yaml_file(json_data):
    workout_name = json_data['workout_name']
    workout_name.replace(" ","")
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
    if(path.exists(workout_name)):
        remove(workout_name)

    return True

