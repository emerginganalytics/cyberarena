import argparse
import os
import time
import googleapiclient.discovery
import calendar
from six.moves import input
from googleapiclient.errors import HttpError
from pprint import pprint



# ------------------------------ parameters ----------------------------------

compute = googleapiclient.discovery.build('compute', 'v1')

project = 'ualr-cybersecurity'
region = 'us-central1'



# --------------------------- create network ----------------------------------

def create_network(name):
    # we first create a network without any subnet
    network_body = {
        "name": name,
        "autoCreateSubnetworks": False,
        "region": "region",
    }

    print("create network", name)

    request = compute.networks().insert(project=project, body=network_body)
    response = request.execute()

    #pprint(response)
    print("Network {} created".format(name))



# --------------------------- create subnet ----------------------------------

# network_name should refer to an existing network
def create_subnet(network_name, subnet_name):
    subnetwork_body = {
        "name" : subnet_name,
        "network": "projects/ualr-cybersecurity/global/networks/" + network_name,
        "ipCidrRange": "10.1.1.0/24",
    }

    request = compute.subnetworks().insert(project=project, region=region, body=subnetwork_body)
    request.execute()

    # print(response)
    print("Subnet {} of network {} created".format(subnetwork_body['name'], network_name))



# --------------------------- add firewall rules ----------------------------------

# first firewall to allow server ports
def create_firewall_allow_server_ports(network_name):
    firewall_body = {
            "name": network_name + "-allow-server-ports",
            "network": "https://www.googleapis.com/compute/v1/projects/ualr-cybersecurity/global/networks/" + network_name,
            "allowed": [
                {
                    "IPProtocol": "tcp",
                    "ports": [
                        "22","8080"
                    ]
                }
            ],
            "sourceRanges": [
                "0.0.0.0/0"
            ]
        }

    request = compute.firewalls().insert(project=project, body=firewall_body)
    request.execute()

    #pprint(response)
    print("Firewall {} created".format(firewall_body['name']))


# first firewall to allow server ports
def create_firewall_allow_internal(network_name):
    firewall_body = {
            "name": network_name + "-allow-internal",
            "network": "https://www.googleapis.com/compute/v1/projects/ualr-cybersecurity/global/networks/" + network_name,
            "allowed": [
                {"IPProtocol": "tcp"},{"IPProtocol": "udp"},{"IPProtocol": "icmp"},
            ],
            "sourceRanges": [
                "10.1.1.0/24"
            ]
        }

    request = compute.firewalls().insert(project=project, body=firewall_body)
    request.execute()

    #pprint(response)
    print("Firewall {} created".format(firewall_body['name']))



# --------------------------- Run ----------------------------------

# this is probably not the best practice...
# but basically we have to wait for a certain amount of time before create a subnetwork
def create_ecosystem_workout(name, ts):

    print("ecosystem creation {}-{}".format(name, ts))
    create_network(name)
    time.sleep(50)

    subnetwork = 'lab-{}-{}'.format(ts, name[-9:])
    print("Network-name : {}, Subnetwork-name : {}".format(name, subnetwork))

    create_subnet(name, subnetwork)
    time.sleep(20)

    create_firewall_allow_server_ports(name)
    create_firewall_allow_internal(name)







