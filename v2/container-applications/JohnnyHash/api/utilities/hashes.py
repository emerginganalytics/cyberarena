from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes
from hashlib import md5
import random


class Hashes:
    def __init__(self, build_id):
        self.build_id = build_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.build_id)
        self.build = self.ds.get()
        if self.build:
            self.passkey = self._generate_passkey()
        else:
            raise ValueError(f'No build found with build_id {self.build_id}')
        self.update = False

    @staticmethod
    def _generate_passkey():
        password = {'rand_pass': '', 'hash': '',}
        # Password format {str}{int}. If len(str) < 8, {int}{str}{int}
        str_list = [
            'Ornn',
            'Hak5',
            'Hacking',
            'BlackHatPython',
            'SpiesAmongUs',
            '9999',
            '1994',
            '5',
            '7',
            '33',
            '19',
            '2020',
            '1234',
            '0000'
        ]
        password['rand_pass'] = random.choice(str_list[0:5])
        password['rand_pass'] += random.choice(str_list[6:14])
        if len(password['rand_pass']) < 8:
            password['rand_pass'] = random.choice(str_list[6:14]) + password['rand_pass']
        password['hash'] = md5(str(password['rand_pass']).encode('UTF-8')).hexdigest()
        return password

    def set_md5_hash(self, question_id):
        if self.build and question_id:
            if self.build.get('escape_room', None):
                for puzzle in self.build['escape_room']['puzzles']:
                    if puzzle['id'] == str(question_id):
                        if puzzle['question'] == '':
                            puzzle['question'] = self.passkey['hash']
                            puzzle['answer'] = self.passkey['rand_pass']
                            self.update = True
                            self.ds.put(self.build)
                            break
            elif self.build.get('assessment', None):
                for question in self.build['assessment']['questions']:
                    if question['id'] == str(question_id):
                        if question['question'] == '':
                            question['question'] = self.passkey['hash']
                            question['answer'] = self.passkey['rand_pass']
                            self.update = True
                            self.ds.put(self.build)
                            break
