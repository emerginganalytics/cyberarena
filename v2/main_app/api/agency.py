from flask import request, json
from flask.views import MethodView
from api.utilities.decorators import admin_required, instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes
from main_app_utilities.command_and_control.build_attack_to_cloud import AttackSpecToCloud
from main_app_utilities.globals import BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Agency(MethodView):
    """
    API to manage the simulated Botnet; Specifically handlers the networ injects
    Each method, requires a build_id that either refers to:
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
        """Handles inject creation requests
            build_id: id of inject to use
            parent_id: id of parent to send inject to
            mode: inject types [attack, weakness]
            args: arguments used to build script
        """
        # Get form data
        recv_data = json.loads(request.data.decode())

        # Parse Form data
        attack_id = recv_data.get('attack_id', None)
        parent_id = recv_data.get('parent_id', None)
        target_machine = recv_data.get('target_machine', None)

        if attack_id and parent_id and target_machine:
            # Validate build and send to datastore
            args = {}
            attack_ds = DataStoreManager(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC, key_id=attack_id).get()
            attack_obj = attack_ds.copy()
            args['target_machine'] = target_machine

            # Set attack scope to either single workspace or entire class
            target_class = recv_data.get('target_class', None)
            if target_class:
                args['target_build_type'] = BuildConstants.BuildType.FIXED_ARENA_CLASS.value
                args['target_id'] = parent_id
            else:
                args['target_id'] = recv_data.get('target_workspace')
                args['target_build_type'] = BuildConstants.BuildType.FIXED_ARENA_WORKSPACE.value

            # Load attack option
            attack_option = recv_data.get('attack_option', None)
            if attack_option:
                print(attack_option)
                for option in attack_ds['args'][1]['Choices']:
                    if attack_option in option:
                        args['option'] = option[attack_option]
                        break
            else:
                default = attack_ds['args'][1]['default']
                for option in attack_ds['args'][1]['Choices']:
                    if default in option:
                        args['option'] = option[default]
                        break
            attack_obj['args'] = args

            # Get parent id and build type
            attack_obj['parent_id'] = parent_id
            attack_obj['parent_build_type'] = recv_data.get('parent_build_type', BuildConstants.BuildType.FIXED_ARENA_CLASS.value)

            # Set inject mode (attack or weakness)
            mode = recv_data.get('mode', 'attack')
            if mode == 'attack':
                attack_obj['mode'] = str(PubSub.BuildActions.CYBER_ARENA_WEAKNESS.value)
            elif mode == 'weakness':
                attack_obj['mode'] = str(PubSub.BuildActions.CYBER_ARENA_WEAKNESS.value)

            # Validate object before sending the request
            attack_to_cloud = AttackSpecToCloud(cyber_arena_attack=attack_obj)
            attack_to_cloud.commit()
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=409, msg='UNABLE TO PROCESS REQUEST').prepare_response()

    @admin_required
    def delete(self, build_id=None):
        """Not needed for current implementations"""
        return self.http_resp(code=405).prepare_response()

    def put(self, build_id=None):
        """Not needed for current implementations"""
        return self.http_resp(code=405).prepare_response()

# [ eof ]
