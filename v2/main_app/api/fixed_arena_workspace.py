from flask import json, request
from flask.views import MethodView
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaWorkspace(MethodView):
    def __init__(self):
        self.kind = DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        args = request.args
        if build_id:
            list_all = args.get('list', None)
            if list_all:
                print(build_id)
                # for list_all, build_id references the parent fixed-arena-class id
                workspaces = DataStoreManager(key_id=self.kind).query(
                    filter_key='parent_id', op='=', value=build_id
                )
            else:
                # query single fixed-arena-workspace with id=build_id
                workspaces = DataStoreManager(key_type=self.kind, key_id=build_id).get()
            # If object exists, return
            if workspaces:
                return self.http_resp(code=200, data=workspaces).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        # Method not allowed
        return self.http_resp(code=405).prepare_response()

    def delete(self):
        # Method not allowed
        return self.http_resp(code=405).prepare_response()

    def put(self):
        # Method not allowed
        return self.http_resp(code=405).prepare_response()
