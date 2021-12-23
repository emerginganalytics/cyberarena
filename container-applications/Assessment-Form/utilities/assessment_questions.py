questions = {
    1: {
        'question': 'Do you know where to find a listing of all your accounts?',
        'help': 'An account is the username and password for logging into a computer',
        'domain': 'AC',
        'capability': 'C001',
        'option': ['Yes', 'No', "I'm not sure"],
        'points': [1, 0, 0]
    },
    2: {
        'question': 'How long ago have you or a third party reviewed the list of users?',
        'help': '',
        'domain': 'AC',
        'capability': 'C001',
        'option': ['Never', 'Over a year ago', 'Within the year', 'I review it at least once a quarter'],
        'points': [0, 5, 9, 10]
    },
    3: {
        'question': 'Does anyone outside of your company have access to your computers?',
        'help': '',
        'domain': 'AC',
        'capability': 'C001',
        'option': ['I don\'t know', 'Yes, and I don\'t trust them very much',
                   'Yes, but I trust them to not share access with anyone else', 'No'],
        'points': [0, 5, 10, 10]
    },
    4: {
        'question': 'Do you have any employees or contractors that have access to systems they really don\'t need?',
        'help': '',
        'domain': 'AC',
        'capability': 'C002',
        'option': ['I don\'t know', 'Yes, and they have much more access than they need',
                   'Yes, but I trust them',
                   'No'],
        'points': [0, 2, 5, 5]
    },
    5: {
        'question': 'How often do you provide temporary access for anyone?',
        'help': '',
        'domain': 'AC',
        'capability': 'C002',
        'option': ['Regularly', 'A few times a month', 'Infrequently', 'Never'],
        'points': [0, 0, 5, 10]
    },
    6: {
        'question': 'Can any contractors access your systems from their home or office?',
        'help': '',
        'domain': 'AC',
        'capability': 'C002',
        'option': ['I don\'t know', 'I don\'t think so', 'Yes, and I\'m not sure how to shut them off',
                   'Yes, but I can control when they have access', 'No'],
        'points': [0, 5, 2, 10, 10]
    },
    7: {
        'question': 'Do you have any software services in the cloud?',
        'help': 'Software services may include any application which requires you to login in through a browser',
        'domain': 'AC',
        'capability': 'C002',
        'option': ['I don\'t know', 'Yes, and I\'m not sure how to manage those accounts',
                   'Yes, but I know how to manage access to the service',
                   'Yes, and I regularly review access logs to the service',
                   'Yes, but only I can access the service', 'No'],
        'points': [0, 2, 0, 10, 10, 10]
    },
    8: {
        'question': 'Do you have a way to identify any sensitive or secret data for your business?',
        'help': 'Sensitive or secret data may include company trade secrets, employee or customer data',
        'domain': 'AC',
        'capability': 'C002',
        'option': ['No', 'Yes, but we may miss some', 'Typically, yes', 'Yes'],
        'points': [0, 8, 8, 10]
    },
    9: {
        'question': 'Do you know where you store personal information?',
        'help': '',
        'domain': 'AC',
        'capability': 'C004',
        'option': ['No', 'I\'m not sure if we do store personal information',
                   'We do not store personal information',
                   'We keep it in a place where everyone has access',
                   'We have a folder or system where personal information is stored'],
        'points': [0, 0, 10, 2, 10]
    },
    10: {
        'question': 'Do you know where to store secret or sensitive information?',
        'help': '',
        'domain': 'AC',
        'capability': 'C004',
        'option': ['No', 'We don\'t really have a lot of secret information',
                   'We have a folder or system that only a few people have access to'],
        'points': [0, 5, 10]
    },
    11: {
        'question': 'Do you log into any of your systems using a generic name or with just a password?',
        'help': '',
        'domain': 'IA',
        'capability': 'C015',
        'option': ['I don\'t know', 'Yes, we have several generic accounts we use for logging in',
                   'We have a few generic accounts, but they are limited to a few devices or users',
                   'We have one or two generic accounts', 'No'],
        'points': [0, 0, 2, 5, 10]
    },
    12: {
        'question': 'Do people have shared accounts they use to login or do they use the same account?',
        'help': '',
        'domain': 'IA',
        'capability': 'C015',
        'option': ['I don\'t know', 'Yes', 'I don\'t believe so', 'We do not allow shared accounts'],
        'points': [0, 0, 5, 10]
    },
    13: {
        'question': 'Do you have any devices or equipment with a default password?',
        'help': '',
        'domain': 'IA',
        'capability': 'C015',
        'option': ['Yes', 'I don\'t know', 'I don\'t think so',
                   'We have a process to change passwords on any new equipment'],
        'points': [0, 0, 2, 5]
    },
    14: {
        'question': 'How do you dispose of computing equipment?',
        'help': '',
        'domain': 'MP',
        'capability': 'C024',
        'option': ['We throw them in the trash', 'We have a recycling service',
                   'They are locked in a container until a service comes to dispose of them'],
        'points': [0, 2, 10]
    },
    15: {
        'question': 'Do you remove any hard drives or other media (e.g., USB drives, SD cards, etc.) for \
                    destruction before disposing computing equipment?',
        'help': '',
        'domain': 'MP',
        'capability': 'C024',
        'option': ['No', 'Sometimes', 'Always'],
        'points': [0, 5, 10]
    },
    16: {
        'question': 'Do you securely erase hard drives through software or physically shred them prior to disposal?',
        'help': '',
        'domain': 'MP',
        'capability': 'C024',
        'option': ['No', 'Sometimes', 'Always'],
        'points': [0, 5, 10]
    },
    17: {
        'question': 'Do you keep the doors on your computer and equipment rooms locked so that only authorized \
                    personnel with a key can access that room?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Yes, almost always', 'Most of the time', 'Only after business hours',
                   'We do not use locks'],
        'points': [10, 8, 5, 0]
    },
    18: {
        'question': 'What kind of locks do you use on your equipment doors?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Mag locks', 'Dead bolts', 'Handle locks', 'We do not have locks'],
        'points': [10, 8, 2, 0]
    },
    19: {
        'question': 'Do you use electronic badge access?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['No', 'Yes'],
        'points': [0, 10]
    },
    20: {
        'question': 'Do office computers automatically lock their screens after a period of inactivity?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Yes', 'No', 'I don\'t know'],
        'points': [10, 0, 0]
    },
    21: {
        'question': 'Do you keep the doors locked to rooms or storage with archives, records, and backup tapes?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Yes', 'No', 'I don\'t know'],
        'points': [10, 0, 0]
    },
    22: {
        'question': 'How many visitors do you have come through your facilities?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['A lot of visitors each day', 'Some regular visitors', 'Not many visitors',
                   'Almost no visitors'],
        'points': [0, 2, 3, 5]
    },
    23: {
        'question': 'Do you have someone at your office most of the time?',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Yes, we have a receptionist to escort visitors',
                   'We usually have someone available to escort visitors',
                   'We rarely have anyone to escort visitors',
                   'Our facilities remain fairly open to visitors without escort'],
        'points': [10, 8, 2, 0]
    },
    24: {
        'question': 'Do you have cameras on you facilities after business hours',
        'help': '',
        'domain': 'PE',
        'capability': 'C028',
        'option': ['Yes, and they automatically alarm upon intruder detection',
                   'Yes, and we frequently monitor for intrusions', 'Yes, but we don\'t look at them very often',
                   'No, but we have a guard, guard dog, or other person monitoring after hours', 'No'],
        'points': [10, 10, 5, 10, 0]
    },
    25: {
        'question': 'Do you have a firewall for each of your business locations',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['No', 'I\'m not sure', 'Yes'],
        'points': [0, 0, 10]
    },
    26: {
        'question': 'Do you manage your firewall or have a managed service provider manger your firewall?',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['No', 'Yes'],
        'points': [0, 10]
    },
    27: {
        'question': 'Do you have some sort of web filtering system that blocks websites with malware?',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['No', 'I\'m not sure', 'Yes'],
        'points': [0, 0, 10]
    },
    28: {
        'question': 'Do you have a VPN set up for home computers to access your business network?',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['Yes, and we have two factor authentication enabled',
                   'Yes, and we use the same username and password that we have to log into the business computers',
                   'No'],
        'points': [10, 2, 0]
    },
    29: {
        'question': 'Do you separate your business networks using a firewall?',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['Yes', 'No'],
        'points': [10, 0]
    },
    30: {
        'question': 'Do you have any servers or computers at your business that can be reached from the Internet \
                    (e.g., web servers, DNS servers, email servers, etc.)?',
        'help': '',
        'domain': 'SC',
        'capability': 'C039',
        'option': ['Yes, and they are protected in a separate network',
                   'Yes, and they are in a single business network', 'No', 'I don\'t know'],
        'points': [10, 5, 0, 0]
    },
    31: {
        'question': 'Do you have automated updates enabled on your computers and equipment?',
        'help': '',
        'domain': 'SI',
        'capability': 'C040',
        'option': ['Yes, all of them', 'Most of them', 'Half of them', 'No', 'I don\'t know'],
        'points': [10, 8, 5, 0, 0]
    },
    32: {
        'question': 'How often do you check for software or firmware patches on your other computing devices \
                    (e.g., networking, control system, or other)?',
        'help': '',
        'domain': 'SI',
        'capability': 'C040',
        'option': ['I don\'t know', 'At least annually', 'At least quarterly', 'At least monthly',
                   'As soon as they come out'],
        'points': [0, 2, 8, 10, 10]
    },
    33: {
        'question': 'How often do you apply software or firmware patches to your servers?',
        'help': '',
        'domain': 'SI',
        'capability': 'C040',
        'option': ['I don\'t know', 'At least annually', 'At least quarterly', 'At least monthly',
                   'As soon as they come out'],
        'points': [0, 2, 5, 10, 10]
    },
    34: {
        'question': 'How often do you apply software or firmware patches to your networking and Internet routing \
                     equipment?',
        'help': '',
        'domain': 'SI',
        'capability': 'C040',
        'option': ['I don\'t know', 'At least annually', 'At least quarterly', 'At least monthly',
                   'As soon as they come out'],
        'points': [0, 2, 5, 10, 10]
    },
    35: {
        'question': 'How often do you apply software of firmware patches to you office computers?',
        'help': '',
        'domain': 'SI',
        'capability': 'C040',
        'option': ['I don\'t know', 'At least annually', 'At least quarterly', 'At least monthly',
                   'As soon as they come out'],
        'points': [0, 2, 5, 10, 10]
    },
    36: {
        'question': 'Do you have antivirus software (i.e, Windows Defender) running on your office computers and \
                    Windows systems?',
        'help': '',
        'domain': 'SI',
        'capability': 'C041',
        'option': ['Yes, all of them', 'Most of them', 'Half of them', 'No', 'I don\'t know'],
        'points': [10, 8, 2, 0, 0]
    },
    37: {
        'question': 'Do you have any security services scanning for malware on your network firewall?',
        'help': '',
        'domain': 'SI',
        'capability': 'C041',
        'option': ['Yes', 'No', 'I don\'t know'],
        'points': [10, 0, 0]
    },
    38: {
        'question': 'Have you added additional security services on your online or cloud services?',
        'help': '',
        'domain': 'SI',
        'capability': 'C041',
        'option': ['Yes', 'No', 'I don\'t know'],
        'points': [10, 0, 0]
    },
    39: {
        'question': 'Do you have any security scanning service for your email?',
        'help': '',
        'domain': 'SI',
        'capability': 'C041',
        'option': ['Yes', 'No', 'I don\'t know'],
        'points': [10, 0, 0]
    },
    40: {
        'question': 'Is your antivirus system configured to scan documents as they are downloaded or loaded from \
                     USB onto the system?',
        'help': '',
        'domain': 'SI',
        'capability': 'C041',
        'option': ['Yes', 'I don\'t know', 'Yes, but we don\'t have it configured all the time', 'No'],
        'points': [10, 0, 5, 0]
    }
}

domains = {
    'AC': {
        'name': 'Access Control',
        'capabilities': {
            'C001': {
                'name': 'Establish system access capabilities',
                'levels': [1, 2, 10, 21],
                'training_modules': ['1.1']
            },
            'C002': {
                'name': 'Control internal system access',
                'levels': [2, 10, 20, 45],
                'training_modules': ['1.2']
            },
            'C004': {
                'name': 'Limit data access to authorized users and processes',
                'levels': [2, 10, 15, 20],
                'training_modules': ['1.3']
            }
        },
        'training_modules': []
    },
    'IA': {
        'name': 'Identification and Authentication',
        'capabilities': {
            'C015': {
                'name': 'Grant access to authenticated entities',
                'levels': [2, 7, 10, 25],
                'training_modules': []
            }
        },
        'training_modules': []
    },
    'MP': {
        'name': 'Media Protection',
        'capabilities': {
            'C024': {
                'name': 'Sanitize media',
                'levels': [2, 10, 15, 30],
                'training_modules': []
            }
        },
        'training_modules': []
    },
    'PE': {
        'name': 'Physical Protection',
        'capabilities': {
            'C028': {
                'name': 'Limit physical access',
                'levels': [10, 25, 50, 75],
                'training_modules': []
            }
        },
        'training_modules': []
    },
    'SC': {
        'name': 'System and Communication Protections',
        'capabilities': {
            'C039': {
                'name': 'Control communications at system boundaries',
                'levels': [5, 15, 30, 60],
                'training_modules': []
            }
        },
        'training_modules': []
    },
    'SI': {
        'name': 'System and Information Integrity',
        'capabilities': {
            'C040': {
                'name': 'Identify and Manage Information System Flaws',
                'levels': [4, 10, 20, 50],
                'training_modules': []
            },
            'C041': {
                'name': 'Identify Malicious Content',
                'levels': [4, 10, 20, 50],
                'training_modules': []
            }
        },
        'training_modules': []
    }
}
