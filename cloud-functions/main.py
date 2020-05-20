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
    workout_type = event['attributes']['workout_type'] if 'workout_type' in event['attributes'] else None
    unit_id = event['attributes']['unit_id'] if 'unit_id' in event['attributes'] else None
    num_team = int(event['attributes']['num_team']) if 'num_team' in event['attributes'] else None
    workout_length = int(event['attributes']['length']) if 'length' in event['attributes'] else None
    email = event['attributes']['email'] if 'email' in event['attributes'] else None
    unit_name = event['attributes']['unit_name'] if 'unit_name' in event['attributes'] else None

    if not workout_type or not unit_id or not num_team or not workout_length:
        if context:
            print("""Invalid fields for pubsub message triggered by messageId {} published at {}
            """.format(context.event_id, context.timestamp))
        return False

    build_workout(workout_type, int(num_team), int(workout_length), unit_id, email, unit_name)

    if context:
        print("""Workout of type {} has completed for user {}. This was triggered by PubSub messageId {} published at {}
        """.format(workout_type, email, context.event_id, context.timestamp))

def cloud_fn_start_vm(event, context):
    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False

    start_vm(workout_id)

    
    


# For local testing
data = \
        {
            'workout_type': 'cyberattack',
            'unit_id': '123456',
            'num_team': '1',
            'length': '1',
            'email': 'pdhuff@ualr.edu',
            'unit_name': 'Testing JSON'
        }
event = {'attributes': data}
cloud_fn_build_workout(event, None)
