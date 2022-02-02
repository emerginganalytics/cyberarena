import os
import sys
import yaml
from common.globals import ds_client, BUILD_STATES, compute, project, student_instructions_url
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition


def update_student_instructions_for_unit(unit_id, instructions_file):
    """
    Update the student instructions with the specified file.
    @param unit_id: The unit to update
    @type unit_id: str
    @param instructions_file: File to use in the Cloud storage under the globally defined student_instructions_url
    @type instructions_file: str
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    for workout in list(query_workouts.fetch()):
        workout['student_instructions_url'] = f"{student_instructions_url}{instructions_file}"
        ds_client.put(workout)

if __name__ == "__main__":
    unit_id = None
    student_instructions = None
    update_student_instructions_for_unit(unit_id, student_instructions)
