from google.cloud import datastore
from utilities.globals import ds_client, myconfig, cloud_log, LogIDs, LOG_LEVELS


class ArenaAuthorizer:
    """
    Used for authorizing and redirecting authenticated users in the application
    Usage:

    arena_auth = ArenaAuthorizer()
    level = arena_auth.check_level(email_address)
    """
    class UserGroups:
        AUTHORIZED = "authorized_users"
        ADMINS = "admins"
        STUDENTS = "students"
        PENDING = "pending"
        ALL_GROUPS = [AUTHORIZED, ADMINS, STUDENTS]

    def __init__(self):
        self.admin_info = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
        if not self.admin_info or self.UserGroups.ADMINS not in self.admin_info:
            if not self.admin_info:
                self.admin_info = datastore.Entity(ds_client.key('cybergym-admin-info', 'cybergym'))
            admin_email_config = myconfig.get_variable('admin_email')
            admin_email = admin_email_config.value.decode("utf-8") if admin_email_config else None
            if not admin_email:
                cloud_log(LogIDs.MAIN_APP, f"Error: Admin Email is not set for this project!", LOG_LEVELS.ERROR)
            else:
                self.admin_info[self.UserGroups.ADMINS] = [admin_email]
        if self.UserGroups.AUTHORIZED not in self.admin_info:
            self.admin_info[self.UserGroups.AUTHORIZED] = []
        if self.UserGroups.STUDENTS not in self.admin_info:
            self.admin_info[self.UserGroups.STUDENTS] = []
        if self.UserGroups.PENDING not in self.admin_info:
            self.admin_info[self.UserGroups.PENDING] = []
        ds_client.put(self.admin_info)

    def get_user_groups(self, user):
        """
        Get the groups this users is authorized under for this Arena
        @param user: Email address of authenticated user
        @type user: str
        @return: List of groups assigned to the user
        @rtype: list
        """
        user_groups = []
        for group in self.UserGroups.ALL_GROUPS:
            if user in self.admin_info[group]:
                user_groups.append(group)

        if not user_groups and user not in self.admin_info[self.UserGroups.PENDING]:
            cloud_log(LogIDs.USER_AUTHORIZATION, f"Unauthorized User: {user}. Adding to pending authorization",
                      LOG_LEVELS.ERROR)
            self.admin_info[self.UserGroups.PENDING].append(user)
            ds_client.put(self.admin_info)

        cloud_log(LogIDs.USER_AUTHORIZATION, f"{user} logged in under groups {user_groups}", LOG_LEVELS.INFO)
        return user_groups
