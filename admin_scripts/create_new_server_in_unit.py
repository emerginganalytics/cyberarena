import os
import sys
import time
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from google.cloud import pubsub_v1
from script_utilities.gcp_credential_manager import GCPCredentialManager
GCPCredentialManager.check_gcp_credentials()
from common.globals import ds_client, PUBSUB_TOPICS, project, SERVER_ACTIONS
from utilities.infrastructure_as_code.server_spec_to_cloud import ServerSpecToCloud

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--unit", default=None, help="Unit ID to build the server in")
parser.add_argument("-s", "--server-spec", default=None, type=str, help="Name of server specification in the "
                                                                         "build-files/server-specs folder")

args = vars(parser.parse_args())

# Set up parameters
unit_id = args['unit']
server_spec = args['server_spec']


def create_new_server_in_unit(unit_id, server_spec_file):
    """
    Use this script when a new server is needed for an existing Unit. This is often helpful for semester long labs
    in which you would like to modify the build environment.
    @param unit_id: The unit_id to add the server to
    @type unit_id: String
    @param server_spec_file: The yaml specification file which holds the new server
    @type server_spec_file: str
    @return: None
    @rtype: None
    """
    spec_folder = "temp"

    # Open and read YAML file
    file_object = os.path.join(spec_folder, server_spec_file)
    try:
        with open(file_object, "r") as f:
            server_spec = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print(f"Error, server spec file {server_spec_file} not found.")
        return

    publisher = pubsub_v1.PublisherClient()
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    print(f"Info: Beginning to send messages to build server {server_spec['name']} in unit {unit_id}.")
    for workout in list(query_workouts.fetch()):
        workout_id = workout.key.name
        workout_project = workout.get('build_project_location', project)
        try:
            cloud_ready_server = ServerSpecToCloud(server_spec=server_spec, build_id=workout_id)
            cloud_ready_server.commit_to_cloud()
        except ValueError:
            print(f"Warning: the server for build {workout_id} already exists")

        topic_path = publisher.topic_path(workout_project, pubsub_topic)
        server_name = f"{workout_id}-{server_spec['name']}"
        publisher.publish(topic_path, data=b'Server Build', server_name=server_name, action=SERVER_ACTIONS.BUILD)
    print(f"Info: Messages to build server {server_spec['name']} have been sent successfully")


if __name__ == "__main__":
    if not server_spec:
        server_spec = str(input(f"What server spec do you want to use? "))
        if not server_spec.endswith(".yaml"):
            server_spec += ".yaml"
    if not unit_id:
        unit_id = str(input(f"What unit ID do you want to add this server to?: "))
    create_new_server_in_unit(unit_id, server_spec)
