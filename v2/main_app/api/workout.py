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
from main_app_utilities.lms.lms_canvas import LMSCanvas

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
            unit_results = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value).query(filters=filters)
            if not unit_results:
                return redirect(url_for('student_app.claim_workout', error=404))
            else:
                unit = unit_results[0]

            workout_id = self._find_existing_workout(unit, email)
            if workout_id:
                return redirect(url_for('student_app.workout_view', build_id=workout_id))
            else:
                return redirect(url_for('student_app.claim_workout', error=406))
        else:
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
                if question_key := recv_data.get('question_key', None):
                    self.logger.info(f"PUT request question response for id {question_key}")
                    print(recv_data)
                    ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=str(build_id))
                    self.workout = ds_workout.get()
                    unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value, key_id=self.workout['parent_id']).get()
                    if self.workout and 'lms_quiz' in self.workout:
                        workout = self._submit_lms_question(unit, self.workout, question_key)
                        ds_workout.put(workout)
                        return self.http_resp(code=200).prepare_response()
                    elif self.workout and 'assessment' in self.workout:
                        response = recv_data.get('response', None)
                        check_auto = recv_data.get('check_auto', False)
                        correct, update = self._evaluate_question(question_key, response, check_auto)
                        if correct and update:
                            ds_workout.put(self.workout)
                        return self.http_resp(code=200, data=self.workout['assessment']).prepare_response()
                    else:
                        self.logger.error(f"Auto assessment error for workout {build_id}. Either the workout is "
                                          f"invalid or the workout has no associated assessment")
                        return self.http_resp(code=404).prepare_response()
        self.logger.error(f"No build_id supplied.")
        return self.http_resp(code=400).prepare_response()

    def _evaluate_question(self, question_key: int, response: str, check_auto=False):
        """
        Loop through the class questions object for the correct question and determine if the response is correct.
        Args:
            question_key (int):
            response (str):

        Returns: Correct (Bool), Update Obj(Bool)
        """
        for question in self.workout['assessment']['questions']:
            if question['id'] == question_key:
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

    def _submit_lms_question(self, unit, workout, question_key):
        """
        Auto assess a question for the LMS based on the unit and question passed in. The workout is an object variable.
        Args:
            unit (Any): Datastore entity
            question_key (str): A unique identifier of the question being auto assessed
        Returns: None
        """
        lms_type = unit['lms_connection']['lms_type']
        url = unit['lms_connection']['url']
        api_key = unit['lms_connection']['api_key']
        course_code = unit['lms_connection']['course_code']
        student_email = self.workout.get('student_email', None)

        if lms_type == BuildConstants.LMS.CANVAS:
            lms = LMSCanvas(url=url, api_key=api_key, course_code=course_code)
        else:
            self.logger.error(f"Unsupported LMS found for unit {workout['id']} when attempting to auto grade "
                              f"for {student_email}")
            raise ValueError("Unsupported LMS unit")

        quiz_key = workout['lms_quiz'].get('quiz_key', None)
        questions = workout['lms_quiz'].get('questions', None)
        answered = False
        for question in questions:
            if question['question_key'] == question_key and not question.get('complete', False):
                added_points = question['points_possible']
                question['complete'] = True
                print(f"Automated assessment submitted for\nUnit:{unit['id']}\n"
                                 f"Question {question['question_text']}\nStudent: {student_email}")

                self.logger.info(f"Automated assessment submitted for\nUnit:{unit['id']}\n"
                                 f"Question {question['question_text']}\nStudent: {student_email}")
                lms.mark_question_correct(quiz_id=quiz_key, student_email=student_email, added_points=added_points)
                answered = True
                break
            elif question['question_key'] == question_key and question.get('complete', False):
                answered = True
                break

        if not answered:
            print(f"Auto assessment submitted for quiz: {workout['lms_quiz']['id']} and "
                  f"student {student_email}, but the question could not be found in the quiz!")
            self.logger.warning(f"Auto assessment submitted for quiz: {workout['lms_quiz']['id']} and "
                                f"student {student_email}, but the question could not be found in the quiz!")
        return workout

    def _find_existing_workout(self, unit, student_email):
        """
        Looks for an existing workout in the unit with the given student email address. If the workout has not been
        built, then build at this time
        Args:
            unit (Datastore): The datastore record of the unit
            student_email (str): email address to look for

        Returns: workout_id:str or None

        """
        workout_filters = [('parent_id', '=', unit['id'])]
        workout_list = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT).query(filters=workout_filters)
        for workout in workout_list:
            if workout.get('student_email', '').lower() == student_email:
                workout_id = workout['id']
                if workout.get('state', WorkoutStates.NOT_BUILT.value) == WorkoutStates.NOT_BUILT.value:
                    self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                            action=str(PubSub.BuildActions.WORKOUT.value),
                                            key_type=str(DatastoreKeyTypes.WORKOUT.value),
                                            build_id=str(workout_id))
                return workout_id

        # No workout was found. Now determine if you need to build a new one. If not, return None.
        max_builds = min(int(self.env.max_workspaces), int(unit['workspace_settings'].get('count', 10000)))
        lms_build = True if 'lms_quiz' in unit else False
        if len(workout_list) < max_builds and not lms_build:
            claimed_by = json.dumps({'student_email': student_email.lower()})
            workout_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                    action=str(PubSub.BuildActions.UNIT.value),
                                    build_id=str(unit['id']), child_id=workout_id,
                                    claimed_by=claimed_by)
            return workout_id
        else:
            return None
