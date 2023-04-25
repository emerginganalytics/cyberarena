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

import random
import string
import time
import yaml
from datetime import datetime, timedelta, timezone
from flask import request, session, url_for, redirect, json
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from main_app_utilities.infrastructure_as_code.schema import EscapeRoomSchema, PuzzleSchema
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants, Buckets
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from main_app_utilities.global_objects.name_generator import NameGenerator


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
        self.env = CloudEnv()
        self.env_dict = self.env.get_env()
        self.bm = BucketManager(env_dict=self.env_dict)
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value, env_dict=self.env_dict)
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
        build_spec = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG, key_id=build_file).get()
        if not build_spec:
            return self.http_resp(code=404, msg=f'The specification for {build_file} does not exist in the cloud '
                                                f'project.').prepare_response()
        build_spec['instructor_id'] = user_email
        build_spec['workspace_settings'] = {
            'count': build_count,
            'registration_required': False,
            'student_emails': [],
            'expires': datetime.strptime(expires, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).timestamp()
        }
        build_spec['join_code'] = ''.join(str(random.randint(0, 9)) for num in range(0, 6))
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, env_dict=self.env_dict, debug=self.debug)
        # Commit build obj into datastore
        build_spec_to_cloud.commit(publish=False)

        # For each generated team name, send workout build request
        build_id = build_spec_to_cloud.get_build_id()
        team_names = NameGenerator(int(build_count)).generate()
        for team in team_names:
            workout_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            self.pubsub_mgr.msg(handler=str(PubSub.Handlers.BUILD.value),
                                action=str(PubSub.BuildActions.UNIT.value),
                                build_id=str(build_id), child_id=workout_id,
                                claimed_by=json.dumps({'team_name': team}))
        if self.debug:
            return self.http_resp(code=200, data={'build_id': build_id}).prepare_response()
        else:
            return redirect(url_for('teacher_app.escape_room', unit_id=build_id))

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
            if unit_action == PubSub.Actions.START.value:
                ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id)
                workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=build_id)
                for workout in workouts:
                    self.pubsub_mgr.msg(handler=str(PubSub.Handlers.CONTROL.value), build_id=str(workout['id']),
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                        action=str(PubSub.Actions.START.value))
                return self.http_resp(code=200).prepare_response()
            if unit_action == PubSub.Actions.START_ESCAPE_ROOM_TIMER.value:
                ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id)
                workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=build_id)
                if workouts:
                    for workout in workouts:
                        self.pubsub_mgr.msg(handler=str(PubSub.Handlers.CONTROL.value), build_id=workout['id'],
                                            cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                            action=str(PubSub.Actions.START.value))
                        workout['escape_room']['start_time'] = datetime.now().timestamp() + 30
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
        self.env = CloudEnv()
        self.env_dict = self.env.get_env()
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.workout: dict = {}
        self.debug = debug

    def get(self, build_id=None):
        """
        Sends back all workout record data to the user with the appropriate fields for the escape room object.
        Args:
            build_id (str): Workout ID

        Returns: HTTP Response

        """
        query_string = request.args
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
            if workout:
                current_time = datetime.now().timestamp()
                time_limit = workout['escape_room']['time_limit']
                start_time = workout['escape_room']['start_time']
                workout['escape_room']['remaining_time'] = time_limit - (current_time - start_time)
                if query_string:
                    if 'status' in query_string:
                        workout['escape_room']['number_correct'] = workout['escape_room']['puzzle_count'] = 0
                        for puzzle in workout['escape_room']['puzzles']:
                            workout['escape_room']['puzzle_count'] += 1
                            if puzzle['correct']:
                                workout['escape_room']['number_correct'] += 1
                            else:
                                # If the question isn't solved, clear the return object
                                puzzle['answer'] = puzzle['reveal'] = ''
                        workout['escape_room']['answer'] = ''
                    return self.http_resp(code=200, data=workout).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        """
        Used to retrieve list of teams associated with a specific join code
        :return: redirect to claim_escape_room route with target parent_id
        """
        form_data = request.form
        join_code = form_data.get('join_code', None)
        if not join_code:
            return self.http_resp(400).prepare_response()
        unit = DataStoreManager(key_id=DatastoreKeyTypes.UNIT.value).query(
            filter_key='join_code', op='=', value=join_code)
        if unit:
            return redirect(url_for('student_app.claim_escape_room', parent=unit[0]['id']))
        return self.http_resp(404).prepare_response()

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
        if not build_id:
            return self.http_resp(code=404, msg="No build ID provided").prepare_response()
        ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id)
        self.workout = ds_workout.get()
        if not self.workout:
            return self.http_resp(code=404, msg="Workout not found").prepare_response()
        if question_id:
            current_time = datetime.now().timestamp()
            time_limit = self.workout['escape_room']['time_limit']
            start_time = self.workout['escape_room']['start_time']
            self.workout['escape_room']['remaining_time'] = time_limit - (current_time - start_time)
            if self.workout['escape_room']['remaining_time'] > 0:
                if escape_attempt:
                    self._evaluate_escape_room_question(response)
                elif response:
                    self._evaluate_puzzle_question(question_id, response)
                else:
                    self._evaluate_auto_question(question_id)
                ds_workout.put(self.workout)

                # Clean up return object
                self.workout['escape_room']['number_correct'] = self.workout['escape_room']['puzzle_count'] = 0
                for puzzle in self.workout['escape_room']['puzzles']:
                    self.workout['escape_room']['puzzle_count'] += 1
                    puzzle['answer'] = ''
                    if puzzle['correct']:
                        self.workout['escape_room']['number_correct'] += 1
                self.workout['escape_room']['answer'] = ''
                return self.http_resp(code=200, data=self.workout).prepare_response()
            else:
                return self.http_resp(code=404, msg="The escape room has no time remaining.").prepare_response()
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

    def _evaluate_auto_question(self, question_id: int):
        puzzles = self.workout['escape_room']['puzzles']
        for puzzle in puzzles:
            if puzzle['id'] == question_id:
                puzzle['correct'] = True
