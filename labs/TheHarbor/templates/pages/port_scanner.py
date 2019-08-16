# This script runs on Python 3
import socket
import threading
import pprint


def tcp_connect(ip, port_number, delay, open_ports, connection):
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.settimeout(delay)
    test = {}
    try:
        tcp_sock.connect((ip, port_number))
        open_ports[port_number] = open_ports.append(port_number)  # Append open ports: ('Open')
        connection[port_number] = port_number
        test[port_number] = '[+] Open...'                         # for debugging purposes only
    except:
        test[port_number] = '[*] Connection Refused...'


def scan_ports(host_ip, delay):
    #  host_ip = '127.0.0.1'
    threads = []        # To run TCP_connect concurrently
    # output = []         # For checking purposes
    open_ports = []     # For checking purposes
    connection = {}     # For Printing purposes

    # check_port = [22, 53, 80, 631, 3306, 5901, 6001, 8080]      # linux vnc ports
    check_port = [135, 445, 1840, 5000]                         # windows ports
    # check_port = [135, 445, 1536, 1537, 1538, 1539, 1541, 1627, 1629, 1644, 1646, 1835, 1840, 1842, 3213, 5000,
    #              5040, 5700, 6463, 6942, 7680, 8884, 9012]      # current internal windows ports

    # Spawning threads to scan ports
    for i in range(10000):
        # print('Spawning threads...')
        t = threading.Thread(target=tcp_connect, args=(host_ip, i, delay, open_ports, connection))
        threads.append(t)

    # Starting threads
    for i in range(10000):
        # print('Starting threads...')
        threads[i].start()

    # Locking the main thread until all threads complete
    for i in range(10000):
        # print('Locking main thread...')
        threads[i].join()

    if sorted(open_ports) == sorted(check_port):
        print(host_ip, 'success')
        return True
    else:
        # pprint.pprint(connection)
        print(host_ip, 'failure')
        print('Listening on: ', open_ports)
        return False

