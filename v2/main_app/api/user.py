from flask import json, session, request, redirect, url_for
from flask.views import MethodView
from api.utilities.decorators import admin_required, instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager

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
        self.http_resp = HttpResponse
        self.ds = DataStoreManager()
        self.user_mgr = ArenaAuthorizer()

    def get(self, user_id=None):
        """
            Returns auth level of current user
        """
        user_email = session.get('user_email', None)
        if user := self.user_mgr.get_user(user_email):
            return json.dumps(user['permissions'])
        else:
            return json.dumps({
                'instructor': False,
                'admin': False,
                'student': False
            })

    @instructor_required
    def post(self):
        json_data = request.json
        if json_data:
            new_user = json_data.get('new_user', None)
            user = json_data.get('user', None)
            groups = json_data.get('groups', None)
            pending = json_data.get('pending', False)
            settings = json_data.get('settings', None)
            if user and groups and pending:
                approve = json_data.get('approve', True)
                user_email = str(user.lower())
                if not self._update_user(user_email, groups, settings, approve):
                    return self.http_resp(code=404, msg='User not found').prepare_response()
            elif new_user and groups:
                user_email = str(new_user.lower())
                self._add_user(user_email, groups, settings=settings)
            elif user and settings:
                if not self._update_settings(user_email=str(user.lower()), settings=settings):
                    return self.http_resp(code=404, msg='No user found!').prepare_response()
                return self.http_resp(code=200, msg='Settings Updated!').prepare_response()
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400, msg='Something went wrong!').prepare_response()

    def _update_user(self, user_email, groups, settings, approve):
        user_groups = self.user_mgr.UserGroups
        if approve:
            permissions = dict()
            for group, value in groups.items():
                key = user_groups[group.upper()].value
                if value:
                    permissions[key] = True
                else:
                    permissions[key] = False
            return self.user_mgr.update_user(email=user_email, permissions=permissions,
                                             settings=settings)
        else:
            self.user_mgr.remove_user(email=user_email)
            return False

    def _update_settings(self, user_email, settings):
        return self.user_mgr.update_user(email=user_email, settings=settings)

    def _add_user(self, user_email, groups, settings):
        user_groups = self.user_mgr.UserGroups
        admin = instructor = student = False
        for group, value in groups.items():
            if group == user_groups.ADMIN.value:
                admin = value
            elif group == user_groups.INSTRUCTOR.value:
                instructor = value
            elif group == user_groups.STUDENT.value:
                student = value
        # Check for any settings
        if settings:
            self.user_mgr.add_user(email=user_email, admin=admin,
                                   instructor=instructor, student=student,
                                   settings=settings)
        else:
            self.user_mgr.add_user(email=user_email, admin=admin,
                                   instructor=instructor, student=student)
