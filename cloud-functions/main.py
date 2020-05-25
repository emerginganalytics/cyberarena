from common.build_workout import build_workout
from common.start_vm import start_vm


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
        print("""Workout %s has completed.""".format(workout_id))


def cloud_fn_start_vm(event, context):
    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_vm(workout_id)


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
