# Simple program to send messages to a listener on other instances
import base64 as b64
import socket
import sys

arg = sys.argv
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def message(host, msg):
    sock.connect((host, 5555))
    sock.send(msg.encode())
    print('Contact Successful!')


host = arg[1]
msg = arg[2] 

# print("host: {}".format(host))
# print("msg: {}".format(msg))
message(host, msg)
