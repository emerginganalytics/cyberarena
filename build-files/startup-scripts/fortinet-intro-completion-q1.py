#!/usr/bin/python3
import os
import requests
import nmap


def check_firewall(target, port_list):
    """
    :param target: The IP address to scan
    :param port_list: List of ports to assess
    :returns: True if all of the ports in the port list are closed on the target machine, otherwise, False.
    """
    scanner = nmap.PortScanner()

    for port in port_list:
        result = scanner.scan(target, str(port))
        try:
            uphosts = result['nmap']['scaninfo']['scanstats']['uphosts']
        except KeyError:
            uphosts = '0'

        print(f'uphosts for port{port} is {uphosts}.')
        if uphosts == '1':
            return False
    return True


def publish(url, question):
    token = os.environ.get(f'WORKOUTKEY{question}')
    workout_id = os.environ.get('WORKOUTID')

    workout = {
        "workout_id": workout_id,
        "token": token,
    }
    requests.post(url, json=workout)


def main():
    port_list = [80, 23, 443, 21, 22, 25, 3389, 110, 445, 139, 143, 53, 135, 3306, 8080, 1723, 111, 995, 993, 5900]
    target = '10.1.1.2'
    url = os.environ.get('URL')
    if not url:
        print("URL environment variable is not set")
        return

    if check_firewall(target, port_list):
        publish(url + "/complete", question=0)
        print("Phase1 Workout Complete")
    else:
        print("Incomplete")


if __name__ == "__main__":
    main()
