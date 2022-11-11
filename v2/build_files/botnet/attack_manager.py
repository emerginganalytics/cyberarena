from attacks import nmap, sqlmap, metasploit
import subprocess
import requests
from cloud_env import *

__author__ = "Ryan Ronquillo"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Ryan Ronquillo"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ryan Ronquillo"
__email__ = "rfronquillo@ualr.edu"
__status__ = "Testing"

class AttackManager:
    def __init__(self, message):
        self.message = message
        self.attack_type = self.message.get("attack_type", None)
        self.build_id = self.message.get("BUILD_ID", None)
        self.build_type = self.message.get("BUILD_TYPE", None)
        self.attack_output = ''

    def msg(self, output):
        requests.post(CloudEnv().telemetry_url, data=output)
        print(f'Published message id {future.result()}')

    def parse_message(self):
        if self.attack_type == 'metasploit':
            attack = metasploit.Metasploit(rhost='127.0.0.1',args={},lhost='127.0.0.1').build_attack()
            self.attack_output = subprocess.run(attack, shell=True, capture_output=True).stdout
        elif self.attack_type == 'nmap':
            attack = nmap.Nmap('127.0.0.1',{}).build_attack()
            self.attack_output = subprocess.run(attack, shell=True, capture_output=True).stdout
        elif self.attack_type == 'sqlmap':
            attack = sqlmap.SQLmap('127.0.0.1',{}).build_attack()
            self.attack_output = subprocess.run(attack, shell=True, capture_output=True).stdout
        else:
            print('This command is invalid.')
        print(self.attack_output)
        self.msg(self.attack_output)