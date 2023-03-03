import copy

from flask import json, session, request, redirect, url_for
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
            admin = True if ArenaAuthorizer.UserGroups.ADMINS.value in user_groups else False
            student = True if ArenaAuthorizer.UserGroups.STUDENTS.value in user_groups else False
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
        json_data = request.json
        if json_data:
            new_user = json_data.get('new_user', None)
            user = json_data.get('user', None)
            groups = json_data.get('groups', None)
            pending = json_data.get('pending', False)
            if user and groups and pending:
                approve = json_data.get('approve', True)
                user = str(user.lower())
                self._update_users(user, pending, groups, approve)
                self.ds.put(self.admin_info, key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cybergym')
            elif new_user and groups:
                user = str(new_user.lower())
                self._add_user(user, groups)
            self.ds.put(self.admin_info, key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cybergym')
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def _update_users(self, user, pending, groups, approve):
        user_groups = self.authorizer.UserGroups

        # Get all project users and add/remove input user from select groups
        admin_info = copy.deepcopy(self.admin_info)
        if approve:
            for group, value in groups.items():
                key = user_groups[group.upper()].value
                if value:
                    admin_info[key].append(user)
                else:
                    if user in admin_info[key]:
                        admin_info[key].remove(user)
            if pending:
                if user in admin_info['pending']:
                    admin_info['pending'].remove(user)
        else:
            if user in admin_info['pending']:
                admin_info['pending'].remove(user)
        # Clean up the new object and return
        for group in user_groups.ALL_GROUPS.value:
            self.admin_info[group] = list(set(admin_info[group]))
        self.admin_info['pending'] = list(set(admin_info['pending']))

    def _add_user(self, user, groups):
        user_groups = self.authorizer.UserGroups
        admin_info = copy.deepcopy(self.admin_info)
        for group, value in groups.items():
            key = user_groups[group.upper()].value
            if value:
                admin_info[key].append(user)
        if user in admin_info['pending']:
            admin_info['pending'].remove(user)
        # Clean up the new object and return
        for group in user_groups.ALL_GROUPS.value:
            self.admin_info[group] = list(set(admin_info[group]))
        self.admin_info['pending'] = list(set(admin_info['pending']))
