#!/usr/bin/python3
import os
import socket

def check_linux_perm():
    filename = '/usr/local/etc/protect_me/vulnerable.txt'
    status = os.stat(filename)
    permissions = oct(status.st_mode)[-3:]

    if permissions == '755':
        print("[+] Permisions: {} --> I'm Secure!".format(permissions))
        return True
    else:
        print("[+] Permissions: {} --> Still vulnerable! ".format(permissions))
        return False

def check_win_perm():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('10.128.0.20', 5555))
    s.listen(5)

    conn, addr = s.accept()
    data = conn.recv(1024).decode('utf-8')

    if data:
        print('[+] Message Received: {}'.format(data))
        s.close()
        return True

# if workout is complete, publish
check_linux = check_linux_perm()
check_windows = check_win_perm()

if check_linux and check_windows:
    print('[*] Publishing Results ...')
    os.system('python3 /usr/local/bin/cg-post.py permissions')
~                                                                                                                                                                        
~                                                                   
