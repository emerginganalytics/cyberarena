from flask import request, json
from flask.views import MethodView
from api.utilities.decorators import instructor_required, admin_required
from api.utilities.http_response import HttpResponse
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import DatastoreKeyTypes
from utilities.command_and_control.attack_spec_to_cloud import AttackSpecToCloud

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AttackSpecs(MethodView):
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
            return self.http_resp(code=404)
        else:
            attack_specs_query = DataStoreManager(key_id=build_id).query()
            attack_specs = list(attack_specs_query.fetch())
            if attack_specs:
                return json.dumps({'data': attack_specs})
            return self.http_resp(code=404)

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
            return json.dumps({'data': filtered_specs})
        return self.http_resp(code=404)

    def delete(self, build_id):
        return self.http_resp(code=405)

    @admin_required
    def put(self, build_id=None):
        recv_data = request.json
        if recv_data.get('update', None):
            AttackSpecToCloud().update()
        return self.http_resp(code=405)

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
