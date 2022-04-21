import os
import sys
import time
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from google.cloud import pubsub_v1
from common.globals import ds_client, PUBSUB_TOPICS, project, SERVER_ACTIONS, BUILD_STATES

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
parser.add_argument("-u", "--unit", default=None, help="Unit ID in which to delete the server")
parser.add_argument("-s", "--server-name", default=None, type=str, help="Name of server to delete (i.e., without "
                                                                        "the workout ID in front)")

args = vars(parser.parse_args())

# Set up parameters
unit_id = args['unit']
server = args['server_name']


def delete_server_in_unit(unit_id, server):
    """
    Use this function to delete a server from each workout in a unit.
    """
    publisher = pubsub_v1.PublisherClient()
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    print(f"Info: Beginning to send messages to delete server {server} in unit {unit_id}.")
    servers = []
    for workout in list(query_workouts.fetch()):
        workout_id = workout.key.name
        workout_project = workout.get('build_project_location', project)
        topic_path = publisher.topic_path(workout_project, pubsub_topic)
        server_name = f"{workout_id}-{server}"
        publisher.publish(topic_path, data=b'Delete', server_name=server_name, action=SERVER_ACTIONS.DELETE)
        servers.append(server_name)
    print(f"Info: Messages to delete servers {server} have been sent successfully. Beginning to delete keys")

    for server_name in servers:
        print(f'Info: Attempting to delete {server_name} record. This will wait to make sure it is deleted')
        deleted = False
        i = 0
        while not deleted and i < 5:
            server_record = ds_client.get(ds_client.key('cybergym-server', server_name))
            if server_record['state'] == BUILD_STATES.DELETED:
                ds_client.delete(server_record.key)
                deleted = True
            else:
                i += 1
                time.sleep(10)
        if i >= 5:
            print(f'Error: timeout when trying to delete {server_name}')


if __name__ == "__main__":
    if not unit_id:
        print("Error: Must supply a unit ID")
    elif not server:
        print("Error: Must supply a server name")
    else:
        delete_server_in_unit(unit_id, server)
