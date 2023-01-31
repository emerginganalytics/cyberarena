from api.utilities.decorators import auth_required, admin_required
from api.utilities.http_response import HttpResponse
from flask import abort, request, json, session
from flask.views import MethodView
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import PubSub, WorkoutStates

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
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.workout: dict = {}

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
                        state = workout.get('state', None)
                        if state:
                            return self.http_resp(code=200, data={'state': state}).prepare_response()
                        else:
                            return self.http_resp(code=200, data={'state': WorkoutStates.RUNNING.name}).prepare_response()
                return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @auth_required
    def post(self, build_id):
        """
        Used for student-initiated build. Otherwise, the workout is built as part of a unit
        Args:
            build_id (str): The ID of the workout to build.

        Returns: str

        """
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
            if workout.get('state', None) == WorkoutStates.READY:
                data = request.json
                workout_id = data.get('workout_id', None)
                # No workout_id given
                if not workout_id:
                    abort(404)
                message = f"Student initiated cloud build for workout {workout_id}"
                self.pubsub_manager.msg(workout_id=workout_id, message=message)
                return self.http_resp(code=200, msg='Workout Built').prepare_response()
            # Bad Request; Already Built
            else:
                return self.http_resp(code=400).prepare_response()
        else:
            auth_level = session.get('user_groups', None)
            if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
                # TODO: Write logic to support standard workout creation requests
                return self.http_resp(code=200).prepare_response()
            else:  # Invalid Request; Insufficient Permissions
                return self.http_resp(code=403).prepare_response()

    def put(self, build_id=None):
        """
        Change build state based on action (START, STOP, NUKE, etc)
        """
        if build_id:
            args = request.args
            if args:  # Check what action is being requested for current workout
                action = args.get('action', None)
                valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value, PubSub.Actions.NUKE.value]
                if action and int(action) in valid_actions:
                    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
                    if workout:
                        self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                                build_id=str(build_id),
                                                cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value))
                        return self.http_resp(code=200, data={'state': workout.get('state')}).prepare_response()
                    return self.http_resp(code=404).prepare_response()
            elif request.json:  # Check if question response is submitted
                recv_data = request.json
                question_id = recv_data.get('question_id', None)
                response = recv_data.get('response', None)
                if question_id and response:
                    ds_workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=str(build_id))
                    self.workout = ds_workout.get()
                    if self.workout:
                        correct = self._evaluate_question(question_id, response)
                        if correct:
                            ds_workout.put(self.workout)
                        # Clean up sensitive data from return object
                        for question in self.workout['assessment']['questions']:
                            question['answer'] = ''
                        return self.http_resp(code=200, data=self.workout['assessment']).prepare_response()
                    return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def _evaluate_question(self, question_id: int, response: str):
        """
        Loop through the class questions object for the correct question and determine if the response is correct.
        Args:
            question_id (int):
            response (str):

        Returns: None

        """
        # TODO: Need to determine the best way to handle assessments with types other than auto
        #       (i.e. upload, manual...)
        for question in self.workout['assessment']['questions']:
            if question['type'] == 'auto':
                if question['id'] == question_id:
                    if not question['complete']:
                        responses = question.get('responses', [])
                        responses.append(response)
                        question['responses'] = responses
                        if question['answer'] == response:
                            question['complete'] = True
                            return True
                    return False
