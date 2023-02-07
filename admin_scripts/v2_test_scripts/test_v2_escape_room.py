import json
from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from main_app_utilities.globals import Buckets, PubSub
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from api.escape_room import EscapeRoomUnit, EscapeRoomWorkout
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.unit import Unit


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


OPTIONS = [
    'Start the escape room timer',
    'Test answering questions in the escape room',
    'Get the contents of the escape room',
    'Delete the escape room'
]


class TestEscapeRoom:
    def __init__(self, build_id=None, debug=True):
        self.env = CloudEnv()
        self.bm = BucketManager()
        self.build_id = build_id if build_id else None
        self.escape_room_unit = EscapeRoomUnit(debug=True)
        self.escape_room_workout = EscapeRoomWorkout(debug=True)

    def build(self):
        expires = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
        build_data = {
            'build_file': 'tefference',
            'expires': expires,
            'build_count': 1,
            'user_email': 'philiphuff7@gmail.com'
        }
        print(f"Posting to build a new escape room")
        http_response = self.escape_room_unit.post(data=build_data)
        http_response = json.loads(http_response)
        self.build_id = http_response['data']['build_id']
        print(f"Beginning to build unit with ID {self.build_id}")
        Unit(build_id=self.build_id, debug=True).build()
        print(f"Sent pubsub message to build unit with ID {self.build_id}")

    def start_escape_room_timer(self):
        data = {
            'unit_action': PubSub.Actions.START_ESCAPE_ROOM_TIMER.value,
            'time_limit': 3600
        }
        http_response = self.escape_room_unit.put(build_id=self.build_id, data=data)

    def attempt_puzzle(self):
        http_response = self.escape_room_unit.get(build_id=self.build_id)
        http_response = json.loads(http_response)
        workout = http_response['data'][0]
        workout_id = workout['id']
        puzzles = []
        for puzzle in workout['escape_room']['puzzles']:
            puzzles.append({
                'id': puzzle['id'],
                'question': puzzle['question']
            })
        while True:
            print(f"Escaped Status: {workout['escape_room']['escaped']}")
            for i, puzzle in enumerate(workout['escape_room']['puzzles']):
                print(f"\tQ{i + 1} Status: Solved={puzzle['correct']}")
            print(f"Questions:")
            for i, puzzle in enumerate(puzzles):
                print(f"  {i + 1}. {puzzle['question']}")
            question_select = int(input(f"Which question number would you like to answer?"))
            response = str(input(f"What is your answer? "))
            http_response = self.escape_room_workout.put(build_id=workout_id,
                                                         question_id=puzzles[question_select - 1]['id'],
                                                         response=response)
            http_response = json.loads(http_response)
            if http_response['status'] == 200:
                workout = http_response['data']
                solved_puzzle = str(input(f"Would you like to attempt and escape(y/N)?"))
                if str.upper(solved_puzzle) == "Y":
                    print(f"Escape Question: {workout['escape_room']['question']}")
                    response = str(input(f"What is your answer?"))
                    http_response = self.escape_room_workout.put(build_id=workout_id, escape_attempt=True,
                                                                 response=response)
                    http_response = json.loads(http_response)
                    workout = http_response['data']
            else:
                print(f"API returned {http_response['status']}: {http_response['message']}")



    def delete(self):
        Unit(build_id=self.build_id, debug=True).delete()


if __name__ == "__main__":
    print(f"Escape Room Tester.")
    delete_first = str(input(f"Do you want to delete a test escape room first? (y/N)"))
    if delete_first and delete_first.upper()[0] == "Y":
        delete_unit = str(input(f"What is the unit ID that you want to delete?"))
        TestEscapeRoom(build_id=delete_unit).delete()
        print(f"Unit deletion was successful!")
    build_first = str(input(f"Do you want to build a new test escape room now? (Y/n)"))
    if not build_first or build_first.upper()[0] == "Y":
        test_unit = TestEscapeRoom()
        test_unit.build()
    else:
        test_unit_id = str(input(f"Which Escape Room unit ID do you want to test?"))
        test_unit = TestEscapeRoom(build_id=test_unit_id)
    while True:
        for i, option in enumerate(OPTIONS):
            print(f"{i + 1}. {option}")
        print(f"99. QUIT")

        option_selection: int = int(input(f"What action are you wanting to test [99]? "))
        if option_selection == 99:
            break
        elif option_selection == 1:
            test_unit.start_escape_room_timer()
        elif option_selection == 2:
            test_unit.attempt_puzzle()
        elif option_selection == 3:
            pass
        elif option_selection == 4:
            test_unit.delete()
