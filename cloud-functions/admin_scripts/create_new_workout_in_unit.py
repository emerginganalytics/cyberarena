
import random
import string
from common.globals import ds_client, BUILD_STATES, compute


def create_new_workout_in_unit(unit_id, student_name, email_address=None, registration_required=False):
    """
    Use this script to add a new workout for a new registered user for a preexising unit
    @param unit_id: The unit_id to add the server to
    @type unit_id: String
    @param student_name: Name of student to add
    @type build_server_spec: String
    @param email_address: Email address of the student to add
    @type build_server_spec: String
    @param registration_required: Whether the new workout requires registration
    @return: None
    @rtype: None
    """
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    workout_template_id = unit['workouts'][0]

    new_workout = ds_client.get(ds_client.key('cybergym-workout', workout_template_id))
    new_id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    new_workout.key = ds_client.key('cybergym-workout', new_id)
    new_workout['state'] = BUILD_STATES.START
    new_workout['student_email'] = email_address
    new_workout['student_name']['student_name'] = student_name
    new_workout['student_name']['student_email'] = email_address
    new_workout['registration_required'] = registration_required

    unit['workouts'].append(new_workout.key.name)

    ds_client.put(unit)
    ds_client.put(new_workout)
    if registration_required:
        print(f"New registered workout created for {email_address}")
    else:
        print(f"New workout ID is {new_id}")
