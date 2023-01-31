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
    API to manage the simulated Botnet; Specifically handler the network injects
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
                injects = DataStoreManager().get_children(child_key_type=self.kind, parent_id=build_id)
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
                attack_obj['mode'] = str(BuildConstants.BuildType.FIXED_ARENA_ATTACK.value)
            elif mode == 'weakness':
                attack_obj['mode'] = str(BuildConstants.BuildType.FIXED_ARENA_WEAKNESS.value)

            # Validate object before sending the request
            attack_to_cloud = AttackSpecToCloud(cyber_arena_attack=attack_obj)
            attack_to_cloud.commit()
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=409, msg='UNABLE TO PROCESS REQUEST').prepare_response()


class AgencyTelemetry(MethodView):
    """
    API to manage the simulated Botnet; Specifically handlers the network injects
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


class AttackSpecs(MethodView):
    """
        API class to handle requests for specific attack specs.
        GET: Returns single attack specification
        POST: Takes input filter string and returns list of all specifications that match
    """
    decorators = [instructor_required]

    def __init__(self):
        self.kind = DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC.value
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        """
        :param build_id:
        :return:
        """
        if build_id:
            attack_spec = DataStoreManager(key_type=self.kind, key_id=build_id).get()
            if attack_spec:
                return json.dumps({'data': attack_spec})
            return self.http_resp(code=404).prepare_response()
        else:
            attack_specs_query = DataStoreManager(key_id=build_id).query()
            attack_specs = list(attack_specs_query.fetch())
            if attack_specs:
                return self.http_resp(code=200, data={'data': attack_specs}).prepare_response()
            return self.http_resp(code=404).prepare_response()

    def post(self):
        """Takes filter items and returns a filtered template list
         Expected filters:
            - attack_name
            - attack_type
            - mitre_attack
            - mode
        """
        recv_data = request.json
        attack_specs = DataStoreManager(key_id=self.kind).query()
        attack_specs = list(attack_specs.fetch())

        filtered_specs = []
        if attack_specs:
            for spec in attack_specs:
                check = self.apply_filter(obj=spec, filters=recv_data)
                if check:
                    filtered_specs.append(spec)
        if filtered_specs:
            return self.http_resp(code=200, data={'data': filtered_specs}).prepare_response()
        return self.http_resp(code=404).prepare_response()

    @staticmethod
    def apply_filter(obj=None, filters=None):
        attack_name = filters.get('attack_name', None)
        attack_type = filters.get('attack_type', None)
        mode = filters.get('mode', None)
        mitre_attack = filters.get('mitre_attack', None)
        # Apply filters
        if attack_name:
            if attack_name.lower() not in obj['attack_name'].lower():
                return False
        if attack_type:
            if attack_type.lower() not in obj['attack_type'].lower():
                return False
        if mode:
            if mode.lower() not in obj['mode'].lower():
                return False
        if mitre_attack:
            if mitre_attack != obj['mitre_attack']:
                return False
        return True

# [ eof ]
