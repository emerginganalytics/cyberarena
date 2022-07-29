from flask import json, request
from flask.views import MethodView
from api.decorators import instructor_required, admin_required
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.gcp.pubsub_manager import PubSubManager
from utilities.gcp.arena_authorizer import ArenaAuthorizer
from utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants

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
        self.actions = PubSub.Actions
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.handler = PubSub.Handlers
        self.states = BuildConstants.FixedArenaStates

    def get(self, build_id=None):
        """Gets fixed-arena object. If build_id and state are in request, view returns
            the fixed-arena state instead"""
        if build_id:
            state = request.args.get('state', None)
            fixed_arena = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value, key_id=build_id).get()
            if fixed_arena:
                if state:
                    return json.dumps({'state': self.states(fixed_arena['state']).name})
                return json.dumps({'fixed_arena': fixed_arena})
            else:
                return "NOT FOUND", 404
        else:
            """Returns list of fixed-arenas in project"""
            fixed_arenas_query = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA.value).query()
            fixed_arenas = list(fixed_arenas_query.fetch())
            if fixed_arenas:
                return json.dumps({'fixed_arena': fixed_arenas})
            return "NOT FOUND", 404

    @admin_required
    def post(self):
        """Create Fixed Arena"""
        recv_data = request.json
        build_id = recv_data.get('build_id', None)
        action = recv_data.get('action', None)

        # Send build/rebuild request
        if build_id and action in [self.actions.BUILD.name, self.actions.REBUILD.name]:
            self.pubsub_manager.msg(handler=PubSub.Handlers.BUILD,
                                    action=self.actions[action], build_id=build_id)
            return "OK", 200
        # Bad request; Either no build_id was found or received an invalid build action
        return "BAD REQUEST", 400

    @admin_required
    def delete(self, build_id=None):
        # Only admins should be allowed to delete an entire fixed-arena
        if build_id:
            self.pubsub_manager.msg(handler=self.handler.CONTROL, action=PubSub.Actions.DELETE, build_id=build_id)
            return "OK", 200
        return "BAD REQUEST", 400

    @instructor_required
    def put(self, build_id=None):
        """
        :parameter build_id: fixed-arena to do action against
        A valid action can be any either START or STOP
        """
        if build_id:
            args = request.args
            action = args.get('action', None)
            valid_actions = [self.actions.START.value, self.actions.STOP.value]
            if action and action in valid_actions:
                self.pubsub_manager.msg(handler=self.handler.CONTROL, action=action, build_id=build_id)
                return "OK", 200
        # Bad request; No build_id given or received an invalid CONTROL action
        return "BAD REQUEST", 400
