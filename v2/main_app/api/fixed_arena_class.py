from flask import json, request
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.gcp.pubsub_manager import PubSubManager
from utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaClass(MethodView):
    # TODO: uncomment for production
    #  decorators = [instructor_required]

    def __init__(self):
        self.kind = DatastoreKeyTypes.FIXED_ARENA_CLASS.value
        self.pubsub_actions = PubSub.Actions
        self.handler = PubSub.Handlers
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        if build_id:
            fa_class = DataStoreManager(key_id=self.kind).query(filter_key='id', op='=', value=build_id)
            if fa_class:
                return json.dumps({'data': fa_class})
            return self.http_resp(code=404)
        return self.http_resp(code=400)

    def post(self):
        recv_data = request.json
        print(recv_data)
        stoc_id = recv_data.get('stoc_id', None)
        build_count = recv_data.get('build_count', None)
        expire_date = recv_data.get('expire_date', None)
        # build_id refers to class template id (I think)
        build_id = recv_data.get('build_id', None)

        # make sure that no running class already exists for fixed-arena
        class_query = DataStoreManager(key_id=self.kind).query()
        class_query.add_filter('parent_id', '=', stoc_id)
        class_query.add_filter('state', '=', str(BuildConstants.FixedArenaClassStates.RUNNING.value))
        check_class = list(class_query.fetch())
        if not check_class:
            print('no class found')
            """TODO: uncomment for production use
            self.pubsub_mgr.msg(handler=self.handler.BUILD, build_id=build_id,
                                action=PubSub.BuildActions.FIXED_ARENA_CLASS,
                                build_count=build_count, expires=expire_date)"""
            return self.http_resp(code=200)
        return self.http_resp(code=409)

    def delete(self, build_id=None):
        if build_id:
            print(f'delete request for {build_id}')
            """ TODO: uncomment for production use
            self.pubsub_mgr.msg(handler=self.handler.CONTROL, build_id=build_id,
                                action=self.pubsub_actions.DELETE,
                                cyber_arena_object=PubSub.CyberArenaObjects.FIXED_ARENA_CLASS)"""
            return self.http_resp(code=200)
        return self.http_resp(code=400)

    def put(self, build_id=None):
        if build_id:
            args = request.args
            action = args.get('action', None)
            valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value]
            if action and action in valid_actions:
                self.pubsub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                    action=PubSub.Actions[action], build_id=build_id)
                return self.http_resp(code=200)
        return self.http_resp(code=400)
