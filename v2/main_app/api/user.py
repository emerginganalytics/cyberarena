from flask import json, session
from flask.views import MethodView
from api.utilities.decorators import admin_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer

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
        self.authorizer = ArenaAuthorizer()
        self.http_resp = HttpResponse

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

    def post(self):
        """Method not needed for current model"""
        return self.http_resp(code=405)

    @admin_required
    def delete(self, user_id=None):
        """
        Method not needed for current model.

        Only admins should be allowed to delete users
        """
        return self.http_resp(code=405)

    @admin_required
    def put(self, user_id=None):
        """
        Method not needed for current model.
        :parameter user_id: user to do action against: authorize or deauth users
        """
        # Bad request
        return self.http_resp(code=405)