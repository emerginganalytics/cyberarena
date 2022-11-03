from attacks import nmap, sqlmap, metasploit
import subprocess
from pubsub_manager import *

class AttackManager:
    def __init__(self, message):
        self.message = message
        self.attack_type = self.message.get("attack_type", None)
        self.attack_output = ''

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
        PubSubManager().msg(self.attack_output)

test = AttackManager({'attack_type':'metasploit'})
test.parse_message()


'''
    def publish(self, attack_log):
        message = {
                'data': attack_log,
                'error': ...
            }
        gcp.publish(msg=json.loads{message}, topic='test')
'''
