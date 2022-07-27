from flask import abort, json, session, request
from flask.views import MethodView
from api.decorators import instructor_required, admin_required
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import PubSub, DatastoreKeyTypes

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
                return json.dumps({'workspaces': workspaces})
            return "NOT FOUND", 404
        return "BAD REQUEST", 400

    def post(self):
        # Method not allowed
        return "NOT ALLOWED", 405

    def delete(self):
        # Method not allowed
        return "NOT ALLOWED", 405

    def put(self):
        # Method not allowed
        return "NOT ALLOWED", 405
