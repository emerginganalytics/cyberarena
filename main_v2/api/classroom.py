import json
from utilities.child_project_manager import ChildProjectManager
from utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud, InvalidBuildSpecification
from utilities.datastore_functions import *
from utilities.workout_validator import WorkoutValidator
from utilities.yaml_functions import YamlFunctions


from flask import request, session, jsonify
from flask.views import View, MethodView
from api.utilities import auth_required, admin_required, instructor_required
from utilities_v2.infrastructure_as_code import build_spec_to_cloud, schema


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Classroom(MethodView):
    decorators = [auth_required]

    def get(self, class_name=None):
        """Get Classroom"""
        if class_name:
            return f'{class_name}'
        return 'CLASSROOM'

    def post(self):
        """Create Classroom"""
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        """Update Existing Classroom"""
        pass
