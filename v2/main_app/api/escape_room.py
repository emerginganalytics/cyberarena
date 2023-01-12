"""
API endpoints for an escape room in the cyber arena. An escape room contains a set of hidden puzzles and codes, and
the team works together to find the locked room code.

This module contains the following classes:
    - EscapeRoomUnit: Used, primarily by the instructor, to interact with a unit of escape rooms.
    - EscapeRoomWorkout: Used, primarily by the team, to interact with individual escape rooms.
"""
__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

import yaml
from datetime import datetime, timedelta, timezone
from flask import request, session
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from main_app_utilities.infrastructure_as_code.schema import EscapeRoomSchema, PuzzleSchema
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants, Buckets
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud


class EscapeRoomUnit(MethodView):
    """
    EscapeRoomUnit is for an instructor or administrator to interact with all workouts in the unit.

    Attributes:
        key_type (int): Datastore record key of type 'unit'

    Methods:
        get: Given a unit ID, this will return all associated workout data
        post: Sets the start_time for each escape room in the unit
    """
    def __init__(self, debug=False):
        self.pubsub_actions = PubSub.Actions
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.bm = BucketManager()
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.env = CloudEnv()
        self.debug = debug

    def get(self, build_id=None):
        if build_id:
            workouts = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id) \
                .get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=build_id)
            if workouts:
                return self.http_resp(code=200, data=workouts).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self, data=None):
        """
        Creates a new unit of escape rooms
        Args:
            data (str): dictionary of build parameters

        Returns: HTTP Response

        """
        if not self.debug:
            data = request.form
            user_email = session.get('user_email', None)
        else:
            user_email = data.get('user_email', None)
        expires = data.get('expires', 2)
        build_file = data.get('build_file', None)
        build_count = data.get('build_count', 1)

        try:
            unit_yaml = self.bm.get(bucket=self.env.spec_bucket, file=f"{Buckets.Folders.SPECS}{build_file}.yaml")
        except FileNotFoundError:
            return self.http_resp(code=404, msg=f"The specification for {build_file} does not exist in the cloud "
                                                f"project.")
        build_spec = yaml.safe_load(unit_yaml)
        build_spec['instructor_id'] = user_email
        build_spec['workspace_settings'] = {
            'count': build_count,
            'registration_required': False,
            'student_emails': [],
            'expires': (datetime.now() + timedelta(days=expires)).timestamp()
        }
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=self.debug)
        build_spec_to_cloud.commit()
        build_id = build_spec_to_cloud.get_build_id()
        return self.http_resp(code=200, data={'build_id': build_id}).prepare_response()

    def put(self, build_id, data=None):
        """
        Start the timer and the workouts similar to the workout functionality.
        Args:
            build_id (str):
            data (dict):

        Returns: HTTP Response with data containing a list of all workouts in the unit with the updated escape room
            parameters.

        """
        if build_id:
            if not self.debug:
                args = request.json
            else:
                args = data
            unit_action = args.get('unit_action', None)
            time_limit = args.get('time_limit', 3600)
            if unit_action == PubSub.Actions.START_ESCAPE_ROOM_TIMER.value:
                ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id)
                workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=build_id)
                if workouts:
                    for workout in workouts:
                        workout['escape_room']['start_time'] = datetime.now().timestamp() + 60
                        workout['escape_room']['time_limit'] = time_limit
                        ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout['id'])
                        ds_workout.put(workout)
                    workouts = workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=build_id)
                    return self.http_resp(code=200, data=workouts).prepare_response()
                return self.http_resp(code=404).prepare_response()
            else:
                self.http_resp(code=501, msg="The requested escape room action is not supported.").prepare_response()
        else:
            return self.http_resp(code=400).prepare_response()


class EscapeRoomWorkout(MethodView):
    """
    EscapeRoomWorkout is for students to interact with escape rooms.

    Attributes:
        key_type (int): Datastore record key of type 'workout'

    Methods:
        get: Given a unit ID, this will return all associated workout data
        post: Sets the start_time for each escape room in the unit
    """
    def __init__(self, debug=False):
        self.key_type = DatastoreKeyTypes.WORKOUT.value
        self.pubsub_actions = PubSub.Actions
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.env = CloudEnv()
        self.workout: dict = {}
        self.debug = debug

    def get(self, build_id=None):
        """
        Sends back all workout record data to the user with the appropriate fields for the escape room object.
        Args:
            build_id (str): Workout ID

        Returns: HTTP Response

        """
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
            if workout:
                current_time = datetime.now().timestamp()
                time_limit = workout['escape_room']['time_limit']
                start_time = workout['escape_room']['start_time']
                workout['escape_room']['remaining_time'] = time_limit - (current_time - start_time)
                return self.http_resp(code=200, data=workout).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def put(self, build_id):
        """
        Team submits responses for checking on both the puzzles and their overall escape room
        Args:
            build_id (str): Workout ID
            escape_attempt (bool): Whether the response represents an escape attempt. If this is provided, the
                question_id can be null
            question_id (str): The UUID of the question being submitted
            response (str): Provided response for the indicated question.

        Returns: HTTP Response

        """
        recv_data = request.json
        escape_attempt = recv_data.get('ea', False)
        question_id = recv_data.get('question_id', None)
        response = recv_data.get('response', None)
        if escape_attempt and escape_attempt == '4534-9a9d':
            question_id = 1
        if build_id and question_id and response:
            ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id)
            self.workout = ds_workout.get()
            if self.workout:
                current_time = datetime.now().timestamp()
                time_limit = self.workout['escape_room']['time_limit']
                start_time = self.workout['escape_room']['start_time']
                self.workout['escape_room']['remaining_time'] = time_limit - (current_time - start_time)
                if self.workout['escape_room']['remaining_time'] > 0:
                    if escape_attempt:
                        self._evaluate_escape_room_question(response)
                    else:
                        self._evaluate_puzzle_question(question_id, response)
                    ds_workout.put(self.workout)
                    return self.http_resp(code=200, data=self.workout).prepare_response()
                else:
                    return self.http_resp(code=404, msg="The escape room has no time remaining.").prepare_response()

            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def _evaluate_escape_room_question(self, response: str):
        """
        Evaluate the final escape room question to determine if it was answered correctly.
        Args:
            response (str): escape room attempt

        Returns: None

        """
        for puzzle in self.workout['escape_room']['puzzles']:
            if not puzzle['correct']:
                return
        self.workout['escape_room']['responses'].append(response)
        if str.upper(response) == str.upper(self.workout['escape_room']['answer']):
            self.workout['escape_room']['escaped'] = True


    def _evaluate_puzzle_question(self, question_id: int, response: str):
        """
        Loop through the class puzzles object for the correct question and determine if the response is correct.
        Args:
            question_id (int):
            response (str):

        Returns: None

        """

        for puzzle in self.workout['escape_room']['puzzles']:
            if puzzle['id'] == question_id and not puzzle['correct']:
                puzzle['responses'].append(response)
                if puzzle['answer'] == response:
                    puzzle['correct'] = True
