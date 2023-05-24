from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer


class UserManger:
    class Commands:
        ADD = (0, 'Add User')
        REMOVE = (1, 'Remove User')
        UPDATE = (2, 'Update User')
        ALL = [ADD, REMOVE, UPDATE]

    class UserLevels:
        ADMIN = (True, True, True)
        INSTRUCTOR = (False, True, True)
        STUDENT = (False, False, True)
        PENDING = (False, False, False)

    def __init__(self):
        self.auth = ArenaAuthorizer()

    def run(self):
        print('--- Cyber Arena User Manger ---')
        while True:
            print('What action would you like to do?')
            for comm in self.Commands.ALL:
                print(f'[{comm[0]}] - {comm[1]}')
            action = int(input('user action > '))
            if action == self.Commands.ADD[0]:
                self._add_user()
            elif action == self.Commands.REMOVE[0]:
                self._remove_user()
            elif action == self.Commands.UPDATE[0]:
                self._update_user()
            cont = str(input('Would you like to do another action? (Y/n)')).lower()
            if cont == 'n':
                break

    def _add_user(self):
        settings = {}
        email = str(input('Enter user email: '))
        print('Permissions Level:\n\t[0] Admin\n\t[1] Instructor\n\t[2] Student')
        user_level = int(input('Select permissions:  '))
        if user_level == 0:
            permissions = self.UserLevels.ADMIN
        elif user_level == 1:
            permissions = self.UserLevels.INSTRUCTOR
        elif user_level == 2:
            permissions = self.UserLevels.STUDENT
            settings = {'canvas': {'api': None, 'url': None}}
        else:
            permissions = self.UserLevels.PENDING
            settings = {'canvas': {'api': None, 'url': None}}
        if user_level in [0, 1]:
            add_api = str(input('Would you like to add an LMS connection at this time? (Y/n)')).lower()
            if add_api == 'y':
                while add_api == 'y':
                    lms, url, api_key = self._get_lms()
                    settings[self.auth.LMS.ALL.value[lms]] = {'api': api_key, 'url': url}
                    add_api = str(input('Add another LMS connection? (Y/n)')).lower()

        self.auth.add_user(
            email=email,
            admin=permissions[0],
            instructor=permissions[1],
            student=permissions[2],
            settings=settings
        )

    def _remove_user(self):
        email = str(input('Email of user you wish to remove: ')).lower()
        if email != '':
            self.auth.remove_user(email=email)

    def _update_user(self):
        email = str(input('Email of user you wish to update: ')).lower()
        settings = {}
        user = self.auth.get_user(email=email)
        print('Current user: ')
        for item in user:
            print(f'\t{str(user[item])}')
        print('\n')

        print('New Permissions Level:\n\t[0] Admin\n\t[1] Instructor\n\t[2] Student')
        user_level = int(input('Select permissions:  '))
        if user_level == 0:
            level = self.UserLevels.ADMIN
        elif user_level == 1:
            level = self.UserLevels.INSTRUCTOR
        elif user_level == 2:
            level = self.UserLevels.STUDENT
            settings = {'canvas': {'api': None, 'url': None}}
        else:
            level = self.UserLevels.PENDING
            settings = {'canvas': {'api': None, 'url': None}}

        if user_level in [0, 1]:
            add_api = str(input('Would you like to add an LMS connection at this time? (Y/n)')).lower()
            if add_api == 'y':
                while add_api == 'y':
                    lms, url, api_key = self._get_lms()
                    settings[self.auth.LMS.ALL.value[lms]] = {'api': api_key, 'url': url}
                    add_api = str(input('Add another LMS connection? (Y/n)')).lower()

        if not level[0] or level[1]:
            clear = True
        else:
            clear = False
        permissions = {'admin': level[0], 'instructor': level[1], 'student': level[2]}
        self.auth.update_user(
            email=email, permissions=permissions,
            settings=settings, clear=clear
        )

    def _get_lms(self):
        for lms in enumerate(self.auth.LMS.ALL.value):
            print(f'{[lms[0]]} - {self.auth.LMS.ALL.value[lms[0]]}')
        lms = int(input("LMS: "))
        url = str(input('LMS URL: '))
        api_key = str(input('API Key: '))
        return lms, url, api_key


if __name__ == '__main__':
    UserManger().run()
