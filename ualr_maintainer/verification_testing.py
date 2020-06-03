'''
def complete_verification():
    if (request.method == 'POST'):
        workout_request = request.get_json(force=True)

        workout_id = workout_request['workout_id']
        token = workout_request['token']
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

        if token in workout['assessment']['questions']:
            question_pos = workout['assessment']['questions'].index(token)
            workout['assessment']['questions'][question_pos]['complete'] = True
            ds_client.put(workout)
            logger.info('%s workout question %d is marked complete.' % (workout_id, question_pos + 1))
            return 'OK', 200
        else:
            logger.info("In complete_verification: Completion key does NOT exist in Questions dict list! Aborting")


assessment:
  type: level
  questions:
    - type: auto
      key: "nA824wazosyssPb1"
      question: "Final task for Mission: Permissions 2"
      script: "MissionPermissions2.py"
      server: missionpermissions2-ubuntu18
      operating-system: linux
      complete: False

'''


def dict_list_query(token):
    workout = {
        'assessment': {
            'questions': [
                {
                    'type': 'auto',
                    'key': 'nA824wazosyssPb1',
                    'question': 'Final task for Mission: Permissions 2',
                    'script': 'MissionPermissions2.py',
                    'server': 'missionpermissions2-ubuntu18',
                    'operating-system': 'linux',
                    'complete': False,
                },
                {
                    'type': 'auto',
                    'key': "ZyjHZdInbnp1iES3",
                    'question': "Final task for Mission: Permissions",
                    'script': "MissionPermissions.ps1",
                    'server': 'missionpermissions2-windows16',
                    'operating-system': 'windows',
                    'complete': False,
                },
                {
                    'type': 'auto',
                    'key': "hxHXan1FFTKaXRkZ",
                    'question': "Final Task for Phishing workout",
                    'script': " ",
                    'server': 'cybergym-phishing',
                    'operating-system': 'linux',
                    'complete': False,
                },
            ]
        },
    }

    token_exists = next(item for item in workout['assessment']['questions'] if item['key'] == token)
    token_pos = next((i for i, item in enumerate(workout['assessment']['questions']) if item['key'] == token), None)
    if token_exists:
        workout['assessment']['questions'][token_pos]['complete'] = True
        print('Token %s exists at question level %d' % (token, token_pos+1))
    else:
        print('Token %s does NOT exist in workout dict list! Aborting.' % token)

    print('Level 1 complete: {}'.format(workout['assessment']['questions'][0]['complete']))
    print('Level 2 complete: {}'.format(workout['assessment']['questions'][1]['complete']))
    print('Level 3 complete: {}'.format(workout['assessment']['questions'][2]['complete']))


token = "nA824wazosyssPb1"
dict_list_query(token)
