#
# This function is a template to use for managing a default inbound rule to ensure the student's IP address class C
# network zone is the only one allowed for the workout.
#

import googleapiclient.discovery
import ipaddress
import time
import calendar
from google.cloud import datastore


# Global variables for this function
from globals import ds_client, compute, project, dnszone, dns_suffix


def student_firewall_add(project, workout_id, ip_address):
    # This pulls the class C subnet of the IP addresse
    ip_subnet = str(ipaddress.ip_network(ip_address + '/24', strict=False))
    ts = str(calendar.timegm(time.gmtime()))

    firewall_body = {
        "name": workout_id + "-external-allow-student-" + ts,
        "network": "https://www.googleapis.com/compute/v1/projects/" + project +  "/global/networks/" +
                   workout_id + "-external-network",
        "allowed": [{"IPProtocol": "tcp"}, {"IPProtocol": "udp"}, {"IPProtocol": "icmp"}],
        "sourceRanges": ip_subnet
        }

    compute.firewalls().insert(project=project, body=firewall_body).execute()
