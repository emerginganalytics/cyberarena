from common.globals import ds_client, BUILD_STATES
from common.compute_management import server_delete
from common.state_transition import state_transition


def fix_student_entry_in_workout(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    print("Starting to delete student entry")
    server_delete(f"{workout_id}-student-guacamole")
    print("Finished deleting student entry")

    guac_connection = []
    if 'connections' in workout['student_entry']:
        network_name = f"{workout_id}-{workout['student_entry']['network']}"
        for entry in workout['student_entry']['connections']:
            connection = create_guac_connection(workout_id, entry)
            guac_connection.append(connection)
    else:
        network_name = f"{workout_id}-{workout['student_entry']['network']}"
        guac_connection.append(create_guac_connection(workout_id, workout['student_entry']))

    print("Starting to build student entry")
    build_guacamole_server(build=workout, network=network_name,
                           guacamole_connections=guac_connection)
    print("Finished sending job to build student entry")


if __name__ == "__main__":
    fix_student_entry_in_workout()
