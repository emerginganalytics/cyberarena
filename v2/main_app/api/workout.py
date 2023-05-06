import random
import string
import time

from api.utilities.http_response import HttpResponse
from datetime import datetime, timedelta, timezone
from flask import abort, request, json, session, redirect, url_for
from flask.views import MethodView
from main_app_utilities.gcp.cloud_logger import Logger

from main_app_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.globals import PubSub, WorkoutStates, BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger", "Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Workout(MethodView):
    def __init__(self):
        self.key_type = DatastoreKeyTypes.WORKOUT.value
        self.env = CloudEnv()
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value, env_dict=self.env.get_env())
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.workout: dict = {}
        self.logger = Logger("main_app.workout").logger

    def get(self, build_id=None):
        """Get Workout Object. This endpoint is accessible to all users. Only authenticated users
        can return the full build object"""
        if build_id:
            args = request.args
            if args.get('all', False):
                workouts = DataStoreManager().get_children(DatastoreKeyTypes.WORKOUT, parent_id=build_id)
                if workouts:
                    return self.http_resp(code=200, data=workouts).prepare_response()
                return self.http_resp(code=404).prepare_response()
            else:
                workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
                if workout:
                    if not args:
                        return self.http_resp(code=200, data=workout).prepare_response()
                    elif args.get('state', False):
                        if state := workout.get('state', None):
                            return self.http_resp(code=200, data={'state': state}).prepare_response()
                        else:
                            return self.http_resp(code=200, data={'state': WorkoutStates.RUNNING.name}).prepare_response()
                return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        """
        Used for student-initiated build. Otherwise, the workout is built as part of a unit
        Args:
            build_id (str): The ID of the unit to a build workout for.

        Returns: str

        """
        form_data = request.form
        email = form_data.get('input_email', None)
        join_code = form_data.get('join_code', None)

        if join_code and email:
            filters = [('join_code', '=', join_code)]
            unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value).query(filters=filters)
            if unit:
                unit_id = unit[0]['id']
                max_builds = min(self.env.max_workspaces, unit[0]['workspace_settings']['count'])
                """workout_query = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT).query()
                workout_list = [i for i in workout_query if i['parent_id'] == unit_id]"""
                workout_list = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT).query(
                    filters=[('parent_id', '=', unit_id)])
                if workout_list:
                    for workout in workout_list:
                        if student_email := workout.get('student_email', None):
                            if email.lower() == student_email:
                                return redirect(url_for('student_app.workout_view', build_id=workout['id']))
                    if len(workout_list) >= max_builds:
                        # build count already meets max build count for unit
                        return redirect(url_for('student_app.claim_workout', error=406))
                # No workout found for given email; Send build request
                claimed_by = json.dumps({'student_email': email.lower()})
                workout_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                        action=str(PubSub.BuildActions.UNIT.value),
                                        build_id=str(unit_id), child_id=workout_id,
                                        claimed_by=claimed_by)
                time.sleep(5)
                return redirect(url_for('student_app.workout_view', build_id=workout_id))
            # Invalid join code
            return redirect(url_for('student_app.claim_workout', error=404))
        return self.http_resp(code=400).prepare_response()

    def put(self, build_id=None):
        """
        Change build state based on action (START, STOP, NUKE, etc)
        """
        if build_id:
            if args := request.args:  # Check what action is being requested for current workout
                action = args.get('action', None)
                valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value, PubSub.Actions.NUKE.value,
                                 PubSub.Actions.EXTEND_RUNTIME.value]
                if action and int(action) in valid_actions:
                    action = int(action)
                    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
                    if workout:
                        if action in [PubSub.Actions.START.value, PubSub.Actions.EXTEND_RUNTIME.value]:
                            if action == PubSub.Actions.EXTEND_RUNTIME.value:
                                duration_hours = 1
                            else:
                                duration_hours = request.json.get('duration', None)
                                try:
                                    duration_hours = min(int(duration_hours), 10)
                                except (TypeError, ValueError):
                                    duration_hours = 2
                            self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                                    build_id=str(build_id), duration=str(duration_hours),
                                                    cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value))
                        elif action in [PubSub.Actions.STOP.value, PubSub.Actions.NUKE.value]:
                            self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                                    build_id=str(build_id),
                                                    cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value))
                        return self.http_resp(code=200, data={'state': workout.get('state')}).prepare_response()
                    return self.http_resp(code=404).prepare_response()
            elif recv_data := request.json:  # Check if question response is submitted
                if question_id := recv_data.get('question_id', None):
                    self.logger.info(f"PUT request question response for id {question_id}")
                    print(f'PUT request question response for id {question_id}')
                    ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=str(build_id))
                    self.workout = ds_workout.get()
                    if self.workout:
                        response = recv_data.get('response', None)
                        check_auto = recv_data.get('check_auto', False)
                        correct, update = self._evaluate_question(question_id, response, check_auto)
                        print(f'Correct: {correct}; Update: {update}')
                        if correct and update:
                            ds_workout.put(self.workout)
                        # Clean up sensitive data from return object
                        for question in self.workout['assessment']['questions']:
                            if question.get('answer', None):
                                question['answer'] = ''
                        return self.http_resp(code=200, data=self.workout['assessment']).prepare_response()
                    return self.http_resp(code=404).prepare_response()
        self.logger.error(f"No build_id supplied.")
        return self.http_resp(code=400).prepare_response()

    def _evaluate_question(self, question_id: int, response: str, check_auto=False):
        """
        Loop through the class questions object for the correct question and determine if the response is correct.
        Args:
            question_id (int):
            response (str):

        Returns: Correct (Bool), Update Obj(Bool)
        """
        for question in self.workout['assessment']['questions']:
            if question['id'] == question_id:
                if question['type'] == 'auto':
                    if check_auto:
                        return question['complete'], False
                    else:
                        question['complete'] = True
                        return True, True
                elif response and not question['complete']:
                    responses = question.get('responses', [])
                    responses.append(response)
                    question['responses'] = responses
                    if question['answer'] == response:
                        question['complete'] = True
                        return True, True
        return False, True

# [ eof ]
