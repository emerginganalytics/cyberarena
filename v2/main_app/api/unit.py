from flask import abort, json, session, request
from flask.views import MethodView
from api.decorators import instructor_required, admin_required
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


class Unit(MethodView):
    """Method View to handle API requests for Cyber Arena Units"""
    decorators = [instructor_required]

    def get(self, build_id=None):
        # TODO: Add GET logic
        args = request.args
        if build_id:
            pass
        # Invalid request; No build_id given
        return "BAD REQUEST", 400

    def post(self):
        # TODO: Add POST logic
        return "BAD REQUEST", 400

    def delete(self):
        # TODO: Add DELETE logic
        return "BAD REQUEST", 400

    def put(self):
        # TODO: Add PUT logic
        return "BAD REQUEST", 400
