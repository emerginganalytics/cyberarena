from common.build_workout import build_workout
from common.delete_expired_workouts import delete_workouts, delete_arenas
from common.start_vm import start_vm, start_arena
from common.stop_compute import stop_everything,stop_lapsed_arenas, stop_lapsed_workouts


def cloud_fn_build_workout(event, context):
    """ Responds to a pub/sub event in which the user has included
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None
    build_workout(workout_id)

    if context:
        print("Workout %s has completed." % workout_id)


def cloud_fn_start_vm(event, context):
    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_vm(workout_id)


def cloud_fn_start_arena(event, context):
    unit_id = event['attributes']['unit_id'] if 'unit_id' in event['attributes'] else None

    if not unit_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_arena(unit_id)


def cloud_fn_delete_expired_workout(event, context):
    """
    Cloud function calls a local function to delete all expired and misfit workouts in the project.
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    delete_workouts()


def cloud_fn_delete_expired_arenas(event, context):
    """
    Cloud function calls a local function to delete all expired and misfit workouts in the project.
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    delete_arenas()

def cloud_fn_stop_all_servers(event, context):
    """
    Simply stops all servers in the project. This is meant to run once a day.
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    stop_everything()


def cloud_fn_stop_lapsed_workouts(event, context):
    """
    Stops expired workouts based on the current time and the number of hours specified to run in the datastore
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    stop_lapsed_workouts()


def cloud_fn_stop_lapsed_arenas(event, context):
    """
    Stops expired arenas based on the current time and the number of hours specified to run in the datastore
    :param event: No data is passed to this function
    :param context: No data is passed to this function
    :return:
    """
    stop_lapsed_arenas()

# Cloud VM Function Testing
# data = \
#     {
#         'workout_id': 'csmymq'
#     }
# event = {'attributes': data}
# cloud_fn_start_vm(event, None)
    


# For local testing
# data = \
#         {
#             'workout_type': 'cyberattack',
#             'unit_id': '123456',
#             'num_team': '1',
#             'length': '1',
#             'email': 'pdhuff@ualr.edu',
#             'unit_name': 'Testing JSON'
#         }
# event = {'attributes': data}
# cloud_fn_build_workout(event, None)
