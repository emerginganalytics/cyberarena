from google.cloud import pubsub_v1
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from common.globals import ds_client, BUILD_STATES, project, WORKOUT_ACTIONS
from utilities.globals import workout_globals
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--unit", default=None, help="Unit ID to nuke and rebuild")

args = vars(parser.parse_args())
unit_id = args['unit']


def nuke_rebuild_unit(unit_id):
    """
    Nukes a full unit. This can be helpful, for example, if you've run out of quota
    :param unit_id: The unit_id to delete
    :param delete_key: Boolean on whether to delete the Datastore entity
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, workout_globals.ps_build_workout_topic)

    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    workouts = list(query_workouts.fetch())
    for (i, workout) in enumerate(workouts):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            print(f"Begin nuking and rebuilding workout {workout.key.name}. This is workout {i} of {len(workouts)}")
            publisher.publish(topic_path, data=b'Cyber Gym Workout', workout_id=workout.key.name,
                              action=WORKOUT_ACTIONS.NUKE)
            print(f"Sent pubsub message to nuke and rebuild workout {workout.key.name}")


if __name__ == "__main__":
    nuke_rebuild_unit(unit_id=unit_id)
