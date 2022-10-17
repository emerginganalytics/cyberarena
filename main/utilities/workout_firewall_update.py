#
# This function is a template to use for managing a default inbound rule to ensure the student's IP address class C
# network zone is the only one allowed for the workout.
#

import ipaddress
import time
import calendar

from googleapiclient.errors import HttpError

# Global variables for this function
from utilities.globals import compute


def student_firewall_add(project, workout_id, ip_address):
    # This pulls the class C subnet of the IP addresse
    ip_subnet = str(ipaddress.ip_network(ip_address + '/24', strict=False))
    ts = str(calendar.timegm(time.gmtime()))

    firewall_body = {
        "name": workout_id + "-external-allow-student-" + ts,
        "network": "https://www.googleapis.com/compute/v1/projects/" + project + "/global/networks/" +
                   workout_id + "-external-network",
        "allowed": [{"IPProtocol": "tcp"}, {"IPProtocol": "udp"}, {"IPProtocol": "icmp"}],
        "sourceRanges": ip_subnet
        }
    try:
        compute.firewalls().insert(project=project, body=firewall_body).execute()
    except HttpError as err:
        # If the network already exists, then this may be a rebuild and ignore the error
        if err.resp.status in [409]:
            pass
