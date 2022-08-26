from flask import request, json
from flask.views import MethodView
from api.utilities.decorators import admin_required, instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Controller(MethodView):
    """
    API to manage the simulated Botnet
    Each method, requires an id, build_id that either refers to:
        - A specific attack (GET, PUT),
        - A fixed-arena to get all attack history from (GET)
        - An attack template to build (POST)
    Only available for users with instructor or greater permissions
    """
    decorators = [instructor_required]

    def __init__(self):
        self.kind = DatastoreKeyTypes.CYBERARENA_ATTACK.value
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        """Retrieve data on either single inject or list of injects for fixed-arena.
           If state is supplied, view returns state of single inject instead"""
        args = request.args
        if build_id:
            # Retrieve inject data
            if args.get('list', None):
                # for a list request, build_id refers to fixed-arena id (parent_id)
                injects_query = DataStoreManager(key_id=self.kind).query()
                injects_query.add_filter('parent_id', '=', build_id)
                injects = list(injects_query.fetch())
                if injects:
                    return self.http_resp(code=200, data={'data': injects}).prepare_response()
            else:
                inject = DataStoreManager(key_type=self.kind, key_id=build_id).get()
                if inject:
                    if args.get('state', False):
                        return json.dumps({'state': inject['state']})
                    return self.http_resp(code=200, data={'data': inject}).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        """Handles inject creation requests"""
        recv_data = request.json
        # Parse Form data
        build_id = recv_data.get('build_id', None)
        network = recv_data.get('network', None)
        mode = recv_data.get('mode', None)
        args = recv_data.get('args', None)
        expires = recv_data.get('expires', None)

        # Send pubsub if all data exists
        if build_id and network and mode and args and expires:
            self.pubsub_manager.msg(handler=PubSub.Handlers.BOTNET, build_id=build_id,
                                    network=network, mode=mode, args=args)
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=409, msg='UNABLE TO PROCESS REQUEST').prepare_response()

    @admin_required
    def delete(self, build_id=None):
        """Not needed for current implementations"""
        return self.http_resp(code=405).prepare_response()

    def put(self, build_id=None):
        """Update Existing Inject"""
        if build_id:
            args = request.args
            action = args.get('action', None)
            # TODO: I'm not sure if we need an expire time for inject objects
            expires = args.get('expires', 2)
            if action in [PubSub.Actions.STOP.value, PubSub.Actions.START.value]:
                self.pubsub_manager.msg(handler=PubSub.Handlers.BOTNET, action=action, expires=expires)
                return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()
