import base64 as b64
import random
import requests

from caesarcipher import CaesarCipher
from google.cloud import datastore
from hashlib import md5


ds_client = datastore.Client()
project = 'ualr-cybersecurity'


def publish_status(workout_id):
    token = "RG987S1GVNKYRYHYA"
    URL = 'https://buildthewarrior.cybergym-eac-ualr.org/complete'

    status = {
        "workout_id": workout_id,
        "token": token,
    }

    publish = requests.post(URL, json=status)
    print('[*] POSTING to {} ...'.format(URL))
    print(publish)


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


'''
    ######### Johnny Hash: Caesar Cipher ###########
    set_ciphers generates a dictionary of casesar cipher 
    base64 value of that cipher and stores the base64
    value in the CyberGym Datastore. The cipher page
    will pull from the Datastore, decode from base64,
    and finally compare the clear text values.
    ###############################################
'''
def set_ciphers(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    result = []
    clear_text = [
        'Something goes to say about how an orange tastes like its color.',
        'Nothing like Java in the morning.',
        'Popping Shells with Powershell.',
        'In security, each minute standing still is another year going backwards.',
        'Aggressively flips open flip phone: "Try hacking me now, buddy"',
        'Help! How do I exit VIM?',
        'Security by obscurity',
        'Disappointed a firewall isn\'t an actual wall of fire',
        'Before anything else, getting ready is the secret of success. - Henry Ford',
        'You can observe a lot by just watching. - Yogi Berra',
        'The Future ain\'t what it used to be. - Yogi Berra',
        'Servers are going down at midnight',
        'The true definition of a keyboard warrior should be a Cybersecurity expert.',
        'Planted 5 O.MG cables in target office',
        'You\'re being followed. Run.',
        'The bird is in the sky.',
        'Nothing hurts more than a missing one ; in 10000 lines of code',
        'Hey Google? How do I vaccinate my computer?',
        'For each coat of paint, a room gets that much smaller.',
    ]

    for pos in range(len(clear_text)):
        key = random.randrange(1, 25)
        cipher_string = CaesarCipher(clear_text[pos], offset=key).encoded
        cipher = b64.b64encode(cipher_string.encode('UTF-8'))

        ciphers = {
            'key': key,
            'cipher': cipher,
            'status': False,
        }
        result.append(ciphers)

    # Selects 3 unique ciphers from list
    cipher_list = random.sample(result, k=3)

    workout['container_info']['cipher_one'] = cipher_list[0]
    workout['container_info']['cipher_two'] = cipher_list[1]
    workout['container_info']['cipher_three'] = cipher_list[2]

    ds_client.put(workout)
    return cipher_list


def check_caesar(workout_id, submission, check):
    # Submission is the plaintext cipher sent from student
    # Cipher_list is the cipher list that is stored in Datastore
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    status = {
        'cipher1': workout['container_info']['cipher_one'],
        'cipher2': workout['container_info']['cipher_two'],
        'cipher3': workout['container_info']['cipher_three'],
    }
    cipher_list = []

    for message in workout['container_info']:
        decoded = (b64.b64decode(message['cipher']).decode('UTF-8'))
        plaintext = CaesarCipher(decoded, offset=message['key']).decoded
        cipher_list.append(plaintext)

    # Possibly Restrict Students from POSTING without all 3 field filled
    if check == 1 and submission in cipher_list:
        status['cipher1']['status'] = True
    if check == 2 and submission in cipher_list:
        status['cipher2']['status'] = True
    if check == 3 and submission in cipher_list:
        status['cipher3']['status'] = True
    # Update Datastore:
    ds_client.put(status)

    if status['cipher1']['status'] and status['cipher2']['status'] and status['cipher3']['status']:
        print('[+] All ciphers are correct!')
        publish_status(workout_id)

    return status

