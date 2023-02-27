import copy

from flask import json, session, request
from flask.views import MethodView
from api.utilities.decorators import admin_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
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


class Users(MethodView):
    def __init__(self):
        self.env = CloudEnv()
        self.authorizer = ArenaAuthorizer(env_dict=self.env.get_env())
        self.http_resp = HttpResponse
        self.ds = DataStoreManager()
        self.admin_info = self.ds.get(key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cybergym')

    def get(self, user_id=None):
        """
            Returns auth level of current user
        """
        user_email = session.get('user_email', None)
        user_groups = self.authorizer.get_user_groups(user_email)
        authorized = admin = False
        if user_groups:
            authorized = True
            admin = True if ArenaAuthorizer.UserGroups.ADMINS in user_groups else False
            student = True if ArenaAuthorizer.UserGroups.STUDENTS in user_groups else False
            response = {
                'authorized': authorized,
                'admin': admin,
                'student': student
            }
            return json.dumps(response)
        else:
            return json.dumps({
                'authorized': False,
                'admin': False,
                'student': False
            })

    @admin_required
    def post(self):
        form_data = request.form
        if form_data:
            user = form_data.get('user', None)
            level = form_data.get('level', None)
            approve = form_data.get('approve', False)
            if user and level and approve:
                user = str(user.lower())
                admin_info = self._update_users(user, approve, level)
                self.ds.put(admin_info, key_id=DatastoreKeyTypes.ADMIN_INFO)
        return self.http_resp(code=405).prepare_response()

    @admin_required
    def delete(self, user_id=None):
        """
        Method not needed for current model.

        Only admins should be allowed to delete users
        """
        return self.http_resp(code=405).prepare_response()

    @admin_required
    def put(self, user_id=None):
        """
        Method not needed for current model.
        :parameter user_id: user to do action against: authorize or deauth users
        """
        # Bad request
        return self.http_resp(code=405).prepare_response()

    def _update_users(self, user, approve, level):
        user_list = dict()
        user_level = self.authorizer.UserGroups

        # Get all project users
        admin_info = copy.deepcopy(self.admin_info)

        # Modify the user object
        if level == user_level.PENDING.value:
            if not approve:
                admin_info['pending'].remove(user)
            else:
                if level == user_level.ADMINS.value:
                    admin_info['admins'].append(user)
                    admin_info['authorized'].append(user)
                    admin_info['students'].append(user)
                elif level == user_level.AUTHORIZED.value:
                    admin_info['authorized'].append(user)
                    admin_info['students'].append(user)
                elif level == user_level.STUDENTS.value:
                    admin_info['students'].append(user)
        if level == user_level.AUTHORIZED.value:
            admin_info['authorized'].append(user)
            admin_info['students'].append(user)
        elif level == user_level.ADMINS.value:
            admin_info['admins'].append(user)
            admin_info['authorized'].append(user)
            admin_info['students'].append(user)

        admin_info['pending'].remove(user)
        return user_list
