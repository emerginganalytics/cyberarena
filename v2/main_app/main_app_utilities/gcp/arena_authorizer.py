import copy
import logging
from google.cloud import logging_v2
from main_app_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from enum import Enum

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ArenaAuthorizer:
    """
        Used for authorizing and redirecting authenticated users in the application
        Usage:

        arena_auth = ArenaAuthorizer()
        level = arena_auth.check_level(email_address)
        """

    class UserGroups(Enum):
        INSTRUCTOR = "instructor"
        ADMIN = "admin"
        STUDENT = "student"
        PENDING = "pending"
        ALL_GROUPS = [INSTRUCTOR, ADMIN, STUDENT]

    class LMS(Enum):
        CANVAS = 'canvas'

    def __init__(self):
        self.log_client = logging_v2.Client()
        self.log_client.setup_logging()
        self.key_type = DatastoreKeyTypes.USERS.value
        self.ds_manager = DataStoreManager()

    def get_all_users(self):
        return DataStoreManager(key_type=self.key_type).query()

    def get_user(self, email):
        return self.ds_manager.get(key_type=self.key_type, key_id=str(email))

    def authorized(self, email, base):
        """
        Checks if supplied user meets the minimum authorization levels.
        args:
            email: str() => email of user to check auth level on
            base: UserGroup(Enum) => lowest level of permitted user authorization
        returns: user obj iff True otherwise False
        """
        if user := self.get_user(email):
            perm = user['permissions']
            if base == self.UserGroups.ADMIN:
                if perm[base.value]:
                    return user
            elif base == self.UserGroups.INSTRUCTOR:
                if perm[self.UserGroups.ADMIN.value] or perm[base.value]:
                    return user
            elif base == self.UserGroups.STUDENT.value:
                if not perm[self.UserGroups.PENDING.value]:
                    return user
        return False

    def _get_admins(self):
        return self.ds_manager.get_admins()

    def _get_user_from_firebase(self, email):
        pass

    def add_user(self, email, **kwargs):
        """
        email: str(email) of user to add
        kwargs:
            admin, instructor, student, pending => optional permissions levels
                if none are supplied, default value is False and pending is set
                to True
            settings: optional dict() e.g {'canvas': APIKEY}; Default value
                is None
        """
        if not email:
            raise ValueError('Missing required field, email, for _add_user method')
        admin = kwargs.get(self.UserGroups.ADMIN.value, False)
        instructor = kwargs.get(self.UserGroups.INSTRUCTOR.value, False)
        student = kwargs.get(self.UserGroups.STUDENT.value, False)
        settings = kwargs.get('settings', {'canvas': None})
        user_obj = {
            'email': str(email),
            'permissions': {
                'admin': admin,
                'instructor': instructor,
                'student': student,
                'pending': False,
            },
            'settings': settings
        }
        if not any(x for x in [admin, instructor, student]):
            user_obj['permissions']['pending'] = True
        self.ds_manager.put(user_obj, key_type=self.key_type, key_id=str(email))
        return True

    def update_user(self, email, permissions=None, settings=None):
        if user := self.get_user(email):
            user_copy = copy.deepcopy(user)
            # Update user permissions
            if permissions:
                for level in permissions:
                    user_copy['permissions'][level] = permissions[level]
            # Update user settings
            if settings:
                for setting in settings:
                    user_copy['settings'][setting] = settings[setting]
            # Make sure pending status is cleared if needed
            perm = user_copy['permissions']
            if perm['admin'] or perm['instructor'] or perm['student']:
                user_copy['permissions']['pending'] = False
            else:
                # No permissions are set for current user; Assume safe to remove all access
                self.remove_user(email=email)
                return True
            # Update user record
            self.ds_manager.put(user_copy, key_type=self.key_type,
                                key_id=str(email))
            return True
        raise ValueError

    def remove_user(self, email):
        # Delete record from Datastore
        self.ds_manager.set(key_type=self.key_type, key_id=str(email))
        self.ds_manager.delete()
        # TODO: Add functionality to search for and
        #  remove user from Firebase db as well
        self._get_user_from_firebase(str(email))
        return True
# [ eof ]
