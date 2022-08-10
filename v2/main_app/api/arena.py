from flask import json, request
from flask.views import MethodView
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import DatastoreKeyTypes, PubSub

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Arena(MethodView):
    def __init__(self):
        # TODO: Get Arena kind
        self.kind = ''
        self.http_resp = HttpResponse
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)

    def get(self, build_id=None):
        if build_id:
            pass
        return self.http_resp(400)

    def post(self):
        return self.http_resp(405)

    def delete(self, build_id=None):
        return self.http_resp(405)

    def put(self, build_id=None):
        if build_id:
            pass
        return self.http_resp(400)
