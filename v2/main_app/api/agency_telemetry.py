from flask import request, json
from flask.views import MethodView
from api.utilities.decorators import admin_required, instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes
from main_app_utilities.command_and_control.build_attack_to_cloud import AttackSpecToCloud

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AgencyTelemetry(MethodView):
    """
    API to manage the simulated Botnet; Specifically handlers the networ injects
    Each method, requires a build_id that either refers to:
        - A specific attack (GET, PUT),
        - A fixed-arena to get all attack history from (GET)
        - An attack template to build (POST)
    Only available for users with instructor or greater permissions
    """

    def __init__(self):
        self.kind = DatastoreKeyTypes.CYBERARENA_ATTACK.value
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.http_resp = HttpResponse
        self.ds = DataStoreManager

    def get(self, build_id=None):
        """Retrieve data on either single inject or list of injects for fixed-arena.
           If state is supplied, view returns state of single inject instead"""
        return self.http_resp(code=404).prepare_response()

    def post(self):
        """Handles inject creation requests
            build_id: id of inject to use
            parent_id: id of parent to send inject to
            mode: inject types [attack, weakness]
            args: arguments used to build script
        """
        recv_data = request.json
        # Parse Form data
        build_id = recv_data.get('build_id', None)
        parent_id = recv_data.get('parent_id', None)
        build_type = recv_data.get('build_type', None)

        # Query for attack object that was created during the initial attack request
        attack_obj = self.ds(key_type=self.kind, key_id=build_id).get()
        log_data = recv_data.get('data', None)

        if build_id and parent_id and log_data:
            # Validate build and send to datastore
            attack_obj['logs'] = attack_obj['logs'].append(log_data)
            attack_obj['errors'] = recv_data.get('errors', 'None')
            attack_obj['status'] = recv_data.get('status', '500')
            attack_obj['mode'] = recv_data.get('mode', 'attack')
            self.ds().put(obj=attack_obj)
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=409, msg='UNABLE TO PROCESS REQUEST').prepare_response()

    def delete(self, build_id=None):
        """Not needed for current implementations"""
        return self.http_resp(code=405).prepare_response()

    def put(self, build_id=None):
        """Not needed for current implementations"""
        return self.http_resp(code=405).prepare_response()

# [ eof ]
