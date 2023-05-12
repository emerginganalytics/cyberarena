import random
from hashlib import md5
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes


class Hashes:
    def __init__(self, build_id=None, workout_info=None):
        self.build_id = build_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=self.build_id)
        if self.build_id and not workout_info:
            self.build = self.ds.get()
        elif workout_info:
            self.build = workout_info
        self.passkey = dict()
        self.update = False

    @staticmethod
    def _generate(password):
        if len(str(password)) <= 20:
            return md5(password.encode('utf-8')).hexdigest()

    def complete(self, question_id):
        if escape_room := self.build.get('escape_room', None):
            for puzzle in escape_room['puzzles']:
                if puzzle['id'] == question_id:
                    puzzle['correct'] = True
                    break
        elif assessment := self.build.get('assessment', None):
            for question in assessment['questions']:
                if question_id == question['id']:
                    question['complete'] = True
                    break
        else:
            raise ValueError(f'Question Not Found with ID :: {question_id}')
        # Update the Workout
        self.ds.put(self.build)

    def set_md5_hash(self):
        if not self.build:
            raise ValueError(f'No build found with build_id {self.build_id}')
        if escape_room := self.build.get('escape_room', None):
            for puzzle in escape_room['puzzles']:
                if puzzle['entry_name'] == 'Johnny Hash':
                    if self._set_md5_passkey(puzzle, True):
                        puzzle['question'] = self.passkey['hash']
                        puzzle['answer'] = self.passkey['password']
                        self.ds.put(self.build)
                    else:
                        # The hash has already been generated, set the passkey obj
                        self._set_md5_passkey(puzzle, False)
                    break
        if assessment := self.build.get('assessment', None):
            question = assessment['questions'][0]
            if self._set_md5_passkey(question, True):
                question['question'] = self.passkey['hash']
                question['answer'] = self.passkey['password']
                self.ds.put(self.build)
            else:
                # The hash has already been generated, set the passkey obj
                self._set_md5_passkey(question, False)
        return self.passkey

    def generate_hashes(self, passwords):
        """
        Takes list of passwords to generates hashes for and returns
        list of key:value (hash, password) pairs
        """
        hash_list = []
        for password in passwords:
            if pass_hash := self._generate(password):
                hash_list.append({
                    'hash': pass_hash,
                    'password': password
                })
            else:
                hash_list.append({
                    'hash': '',
                    'password': password,
                    'error': 'Passwords cannot be longer than 20 characters!'
                })
        return hash_list

    def get_assessment(self):
        if escape_room := self.build.get('escape_room', None):
            for puzzle in escape_room['puzzles']:
                if puzzle['entry_name'] == 'Johnny Hash':
                    return puzzle
        elif assessment := self.build.get('assessment', None):
            return assessment['questions'][0]

    def _generate_md5_passkey(self):
        # Password format {str}{int}. If len(str) < 8, {int}{str}{int}
        password = {'password': '', 'hash': ''}
        str_list = [
            'Ornn', 'Hak5', 'Hacking',
            'BlackHatPython', 'SpiesAmongUs', '9999',
            '1994', '5', '7', '33', '19', '2020', '1234', '0000'
        ]
        password['password'] = random.choice(str_list[0:5])
        password['password'] += random.choice(str_list[6:14])
        if len(password['password']) < 8:
            password['password'] = random.choice(str_list[6:14]) + password['password']
        password['hash'] = self._generate(str(password['password']))
        self.passkey = password

    def _set_md5_passkey(self, question, update):
        """
        Takes the input question_id and verifies that a hash has already been generated for
        that question. If no hash is found, the function will generate a random hash
        :param question: dict()
        :param question_id: Unique Question Identifier to check for generated hash
        :return: Bool(False if already populated or question_id doesn't match)
        """
        if question['question'] in ['', 'HashPlaceholder'] and update:
            # question isn't populated; Generate key
            self._generate_md5_passkey()
            return True
        elif question and not update:
            self.passkey['hash'] = question['question']
            self.passkey['password'] = question['answer']
        return False

    def get_password(self):
        assessment = self.get_assessment()
        return assessment['answer']

# [ eof ]
