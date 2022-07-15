from flask import abort, json, session, request
from flask.views import MethodView
from api.decorators import admin_required, instructor_required
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.gcp.pubsub_manager import PubSubManager
from utilities.gcp.arena_authorizer import ArenaAuthorizer
from utilities.globals import PubSub, DatastoreKeyTypes

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArena(MethodView):
    def __init__(self):
        self.authorizer = ArenaAuthorizer()

    def get(self, build_id=None):
        """Get Fixed Arena"""
        user_email = session.get('user_email', None)
        user_group = session.get('user_group', None)
        if build_id:
            fixed_arena = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT.value, key_id=build_id).get()
            server_query = DataStoreManager(key_id=DatastoreKeyTypes.SERVER.value).query()
            server_query.add_filter('parent_id', '=', build_id)
            server_list = list(server_query.fetch())
            if user_email and fixed_arena['registration_required']:
                if user_email == fixed_arena['student_email'] or self.authorizer.UserGroups.AUTHORIZED in user_group:
                    return json.dumps({'fixed_arena': fixed_arena, 'workstations': server_list})
                # Bad Request; Unauthorized User
                else:
                    abort(403)
            else:
                return json.dumps({'state': fixed_arena['state'], 'workstations': server_list})
        # Bad request; No build_id given
        abort(400)

    @instructor_required
    def post(self, build_id=None):
        """Create Fixed Arena"""
        pass

    @instructor_required
    def delete(self, build_id=None):
        # Instructors should be allowed to delete machines on an existing STOC network
        user_email = session.get('user_email', None)
        user_group = session.get('user_group', None)
        if build_id:
            pass
        else:
            # Only admins should be allowed to delete an entire STOC network
            if self.authorizer.UserGroups.ADMINS in user_group:
                pass
            else:
                abort(403)

    @instructor_required
    def put(self, build_id=None):
        """
        :parameter build_id: Machine to do action against. If no build_id is given
         action is done against fixed network instead.
         Actions can be any of the following: Start, Stop, Restart, or Nuke (Rebuild)
        """
        # Action on specific server
        recv_data = request.json
        action = recv_data.get('action', None)
        if action:
            if build_id:
                pass
            # Action on Fixed Arena
            else:
                if action == PubSub.WorkoutActions.NUKE:
                    PubSubManager(topic=PubSub.Topics.BUILD_ARENA.value).msg(action=action, data=recv_data, build_type='FIXED_ARENA')
                else:
                    PubSubManager(topic=PubSub.Topics.BUILD_ARENA.value, data=recv_data, built_type='FIXED_ARENA')
        else:
            abort(400)