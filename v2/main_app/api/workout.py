from api.utilities.decorators import auth_required, admin_required
from api.utilities.http_response import HttpResponse
from flask import abort, request, json, session
from flask.views import MethodView
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import PubSub

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Workout(MethodView):
    def __init__(self):
        self.topic = DatastoreKeyTypes.CYBERGYM_WORKOUT.value
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        """Get Workout Object. This endpoint is accessible to all users. Only authenticated users
        can return the full build object"""
        if build_id:
            user_email = session.get('user_email', None)
            user_group = session.get('user_group', None)
            workout = DataStoreManager(key_type=self.topic, key_id=build_id).get()
            if workout:
                if user_email and workout['registration_required']:
                    if user_email == workout['student_email'] or ArenaAuthorizer.UserGroups.AUTHORIZED in user_group:
                        return json.dumps(workout)
                    # Bad Request; Unauthorized User
                    else:
                        return self.http_resp(code=403)
                else:
                    # Anonymous user, return only workout state
                    workout_state = workout.get('state', None)
                    if workout_state:
                        return self.http_resp(code=200, msg=workout_state)
                    else:
                        return self.http_resp(code=200, msg="RUNNING")
            # Bad Request; Workout not found
            return self.http_resp(code=404)
        # Bad Request; No build_id given
        return self.http_resp(code=400)

    @auth_required
    def post(self, build_id):
        """Create Workout"""
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=build_id).get()
            if workout['state'] == 'READY':
                data = request.json
                workout_id = data.get('workout_id', None)
                # No workout_id given
                if not workout_id:
                    abort(404)
                message = f"Student initiated cloud build for workout {workout_id}"
                self.pubsub_manager.msg(workout_id=workout_id, message=message)
                return 'Workout Built'
            # Bad Request; Already Built
            else:
                return self.http_resp(code=400)
        else:
            auth_level = session.get('user_groups', None)
            if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
               # TODO: Write logic to support standard workout creation requests
                return self.http_resp(code=200)
            # Invalid Request; Insufficient Permissions
            else:
                return self.http_resp(code=403)

    @admin_required
    def delete(self):
        return self.http_resp(code=405)

    def put(self, build_id=None):
        """
        Change build state based on action (START, STOP, NUKE, etc)
        """
        args = request.args
        if build_id:
            action = args.get('action', None)
            if action:
                # Control request sent for a specific server
                if args.get('manage_server', False):
                    self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=action, build_id=build_id,
                                            cyber_arena_object=PubSub.CyberArenaObjects.SERVER)
                else:
                    # Request to start entire workout
                    if action == PubSub.Actions.NUKE.value:
                        handler = PubSub.Handlers.BUILD
                    else:
                        handler = PubSub.Handlers.CONTROL
                    self.pubsub_manager.msg(handler=handler, build_id=build_id, action=action,
                                            cyber_arena_object=PubSub.CyberArenaObjects.WORKOUT)
                return self.http_resp(code=200)
        return self.http_resp(code=400)
