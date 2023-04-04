import logging
from google.cloud import logging_v2
from main_app_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from main_app_utilities.gcp.cloud_env import CloudEnv
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
        AUTHORIZED = "authorized_users"
        ADMINS = "admins"
        STUDENTS = "students"
        PENDING = "pending"
        ALL_GROUPS = [AUTHORIZED, ADMINS, STUDENTS]

    def __init__(self, env_dict=None):
        self.log_client = logging_v2.Client()
        self.log_client.setup_logging()
        self.ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.ADMIN_INFO.value, key_id='cybergym')
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.admin_info = self.ds_manager.get()
        if not self.admin_info:
            self.admin_info = {}
        if self.UserGroups.ADMINS.value not in self.admin_info:
            admin_email = self.env.admin_email  # myconfig.get_variable.config('admin_email')
            if not admin_email:
                logging.error(msg='Error: Admin Email is not set up for this project!')
            else:
                self.admin_info[self.UserGroups.ADMINS.value] = [admin_email]
        if self.UserGroups.AUTHORIZED.value not in self.admin_info:
            self.admin_info[self.UserGroups.AUTHORIZED.value] = []
        if self.UserGroups.STUDENTS.value not in self.admin_info:
            self.admin_info[self.UserGroups.STUDENTS.value] = []
        if self.UserGroups.PENDING.value not in self.admin_info:
            self.admin_info[self.UserGroups.PENDING.value] = []
        self.ds_manager.put(self.admin_info)

    def get_user_groups(self, user):
        """
        Get the groups this user is authorized under for this Arena
        @param user: Email address of authenticated user
        @type user: str
        @return: List of groups assigned to the user
        @rtype: list
        """
        user_groups = []
        for group in self.UserGroups.ALL_GROUPS.value:
            if user in self.admin_info[group]:
                user_groups.append(group)

        if not user_groups and user not in self.admin_info[self.UserGroups.PENDING.value]:
            logging.error(msg=f'Unauthorized user: {user}. Adding to pending authorization')
            self.admin_info[self.UserGroups.PENDING.value].append(user)
            self.ds_manager.put(self.admin_info)

        logging.debug(f'{user} logged in under groups {user_groups}')
        return user_groups

    def get_aggregated_list(self):
        """
        Get dict of each user with collection of authorized groups for that user
        :return: Dict of users with list of groups assigned to the user
        """
        users = dict()

        for user in self.admin_info['admins']:
            uid = user.lower()
            users[uid] = []
            users[uid].append(self.UserGroups.ADMINS.value)
        for user in self.admin_info['authorized_users']:
            uid = user.lower()
            if not users.get(uid, None):
                users[uid] = []
            users[uid].append(self.UserGroups.AUTHORIZED.value)
        for user in self.admin_info['students']:
            uid = user.lower()
            if not users.get(uid, None):
                users[uid] = []
            users[uid].append(self.UserGroups.STUDENTS.value)
        for user in self.admin_info['pending']:
            uid = user.lower()
            if not users.get(uid, None):
                users[uid] = []
                users[uid].append(self.UserGroups.PENDING.value)
        return users
