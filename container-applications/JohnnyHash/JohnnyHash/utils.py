from globals import ds_client
from hashlib import md5

import random
'''
    ########### Johnny Hash: MD5 CTF ############## 
    gen_pass is called to randomly generate a password
    from a preset list of values. The password and hash
    is stored by calling set_md5_pass. 

    The login page will verify each login attempt with
    the value in the Datastore for that workout_id
    ##############################################
'''


def gen_pass(workout_id):
    password = {
        'rand_pass': '',
        'hash': '',
    }

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

    set_md5_pass(workout_id, password)


def set_md5_pass(workout_id, password):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    workout['container_info']['correct_password'] = password['rand_pass']
    workout['container_info']['correct_password_hash'] = password['hash']

    ds_client.put(workout)
