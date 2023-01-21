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
        self.topic = DatastoreKeyTypes.WORKOUT.value
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        """Get Workout Object. This endpoint is accessible to all users. Only authenticated users
        can return the full build object"""
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
            if workout:
                args = request.args
                if not args:
                    return self.http_resp(code=200, data=workout).prepare_response()
                elif args.get('state', False):
                    state = workout.get('state', None)
                    if state:
                        return self.http_resp(code=200, data={'state': WorkoutStates(state).name}).prepare_response()
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
        # TODO: Update this method to match current v2 directive
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
                return self.http_resp(code=400)
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
        args = request.args
        if build_id:
            action = args.get('action', None)
            valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value, PubSub.Actions.NUKE.value]
            if action and action in valid_actions:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                        build_id=str(build_id),
                                        cyber_arena_object=PubSub.CyberArenaObjects.WORKOUT.value)
                return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400)
