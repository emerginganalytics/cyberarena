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
            workouts = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value, key_id=build_id).get_workouts()
            if workouts:
                return self.http_resp(code=200, data=workouts).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self, recv_data=None):
        """
        Creates a new unit of escape rooms
        Returns: HTTP Response

        """
        if not self.debug:
            recv_data = request.form
            user_email = session.get('user_email', None)
        expires = recv_data.get('expires', 2)
        build_file = recv_data.get('build_file', None)
        build_count = recv_data.get('build_count', 1)

        unit_yaml = self.bm.get(bucket=self.env.spec_bucket, file=f"{Buckets.Folders.SPECS}{build_file}.yaml")
        build_spec = yaml.safe_load(unit_yaml)
        build_spec['instructor_id'] = user_email
        build_spec['workspace_settings'] = {
            'count': build_count,
            'registration_required': False,
            'student_emails': [],
            'expires': (datetime.now() + timedelta(days=expires)).timestamp()
        }
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec)
        build_spec_to_cloud.commit()
        build_id = build_spec_to_cloud.get_build_id()
        return self.http_resp(code=200, data={'build_id': build_id}).prepare_response()

    def put(self, build_id):
        """
        Start the timer and the workouts similar to the workout functionality.
        Returns: HTTP Response

        """
        if build_id:
            args = request.json
            unit_action = args.get('unit_action', None)
            time_limit = args.get('time_limit', 3600)
            if unit_action == PubSub.Actions.START_ESCAPE_ROOM_TIMER.value:
                workouts = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value, key_id=build_id).get_workouts()
                if workouts:
                    for workout in workouts:
                        escape_room_spec: EscapeRoomSchema = EscapeRoomSchema().load(workout['escape_room'])
                        escape_room_spec.start_time = datetime.now().timestamp() + 60
                        escape_room_spec.time_limit = time_limit
                        workout['escape_room'] = escape_room_spec
                        ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout.key)
                        ds_workout.put(workout)
                    return self.http_resp(code=200).prepare_response()
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
        self.puzzles: list = []
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
                escape_room: EscapeRoomSchema = EscapeRoomSchema().load(workout['escape_room'])
                current_time = datetime.now().timestamp()
                escape_room.remaining_time = escape_room.time_limit - (current_time - escape_room.start_time)
                workout['escape_room'] = escape_room
                return self.http_resp(code=200, data=workout).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def put(self, build_id: str = None, question_id: int = None, response: str = None):
        """
        Team submits responses for checking on both the puzzles and their overall escape room
        Args:
            build_id (str): Workout ID
            question_id (str): The UUID of the question being submitted
            response (str): Provided response for the indicated question.

        Returns: None

        """
        if build_id and question_id and response:
            ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id)
            workout = ds_workout.get()
            if workout:
                escape_room: EscapeRoomSchema = EscapeRoomSchema().load(workout['escape_room'])
                current_time = datetime.now().timestamp()
                escape_room.remaining_time = escape_room.time_limit - (current_time - escape_room.start_time)
                if escape_room.remaining_time > 0:
                    self.puzzles = escape_room.puzzles
                    self._evaluate_question(question_id, response)
                workout['escape_room'] = escape_room
                ds_workout.put(workout)
                return self.http_resp(code=200, data=workout).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def _evaluate_question(self, question_id: int, response: str):
        """
        Loop through the class puzzles object for the correct question and determine if the response is correct.
        Args:
            question_id (int):
            response (str):

        Returns:

        """

        for item in self.puzzles:
            puzzle: PuzzleSchema = PuzzleSchema().load(item)
            if puzzle.id == question_id and not puzzle.correct:
                puzzle.responses.append(response)
                if puzzle.answer == response:
                    puzzle.correct = True
        return
