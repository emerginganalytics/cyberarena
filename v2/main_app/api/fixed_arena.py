from flask import json, request
from flask.views import MethodView
from api.utilities.decorators import instructor_required, admin_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants

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
        self.http_resp = HttpResponse
        self.actions = PubSub.Actions
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.handler = PubSub.Handlers
        self.states = BuildConstants.FixedArenaStates

    @instructor_required
    def get(self, build_id=None):
        """Gets fixed-arena object. If build_id and state are in request, view returns
            the fixed-arena state instead"""
        if build_id:
            state = request.args.get('state', None)
            fixed_arena = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value, key_id=build_id).get()
            if fixed_arena:
                if state:
                    return self.http_resp(code=200, data={'state': self.states(fixed_arena["state"]).name}).prepare_response()
                return self.http_resp(code=200, data={'fixed_arena': fixed_arena}).prepare_response()
            else:
                return self.http_resp(code=404).prepare_response()
        else:
            """Returns list of fixed-arenas in project"""
            fixed_arenas_query = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA.value).query()
            fixed_arenas = list(fixed_arenas_query.fetch())
            if fixed_arenas:
                return self.http_resp(code=200, data={'fixed_arena': fixed_arenas}).prepare_response()
            return self.http_resp(code=404).prepare_response()

    @admin_required
    def post(self):
        """Create Fixed Arena"""
        recv_data = request.json
        build_id = recv_data.get('build_id', None)
        action = recv_data.get('action', None)
        # Send build/rebuild request
        if build_id and action in [str(self.actions.BUILD.value), str(self.actions.REBUILD.value)]:
            self.pubsub_manager.msg(handler=PubSub.Handlers.BUILD,
                                    action=self.actions[action], build_id=build_id)
            return self.http_resp(code=200).prepare_response()
        # Bad request; Either no build_id was found or received an invalid build action
        return self.http_resp(code=400).prepare_response()

    @admin_required
    def delete(self, build_id=None):
        # Only admins should be allowed to delete an entire fixed-arena
        if build_id:
            print(f'delete request for {build_id}')
            """self.pubsub_manager.msg(handler=self.handler.CONTROL, action=PubSub.Actions.DELETE, build_id=build_id)"""
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def put(self, build_id=None):
        """
        :parameter build_id: fixed-arena to do action against
        A valid action can be any either START or STOP
        """
        valid_actions = [self.actions.START.value, self.actions.STOP.value]
        args = request.json
        action = args.get('action', None)

        # Action against single fixed-arena or multiple
        if action and action in valid_actions:
            if build_id:
                self.pubsub_manager.msg(handler=self.handler.CONTROL, action=action, build_id=build_id)
                return self.http_resp(code=200).prepare_response()
            else:
                if 'stoc_ids' in args:
                    for stoc_id in args['stoc_ids']:
                        self.pubsub_manager.msg(handler=self.handler.CONTROL, action=action, build_id=stoc_id)
                        print(f'{action} for stoc, {stoc_id}')
                    return self.http_resp(code=200).prepare_response()
        # Bad request; No build_id given or received an invalid CONTROL action
        return self.http_resp(code=400).prepare_response()
