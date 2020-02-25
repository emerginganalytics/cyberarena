#
# This script is intended to be copied into the landing page application for the button click when
# resuming a workout which has previously been stopped.
#
import googleapiclient.discovery
from datetime import datetime, timedelta, date
from google.cloud import datastore
import time
import calendar

# Global variables for this function
ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
expired_workout = []
project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'

# Create a new DNS record for the server and add the information to the datastore for later management
def register_workout_update(project, dnszone, workout_id, old_ip, new_ip):
    service = googleapiclient.discovery.build('dns', 'v1')

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    change_body = {
        "deletions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": workout_id + ".cybergym-eac-ualr.org.",
                "rrdatas": [old_ip],
                "type": "A",
                "ttl": 30
            }
        ],
        "additions": [
        {
            "kind": "dns#resourceRecordSet",
            "name": workout_id + ".cybergym-eac-ualr.org.",
            "rrdatas": [new_ip],
            "type": "A",
            "ttl": 30
        }
    ]}

    request = service.changes().create(project=project, managedZone=dnszone, body=change_body)
    response = request.execute()


    workout["external_ip"] = new_ip
    ds_client.put(workout)



def start_workout(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    try:
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().start(project=project, zone=zone, instance=vm_instance["name"]).execute()
                compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

                if 'accessConfigs' in vm_instance['networkInterfaces'][0]:
                    ip_address = vm_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                    register_workout_update(project, dnszone, workout, workout["external_ip"], ip_address)
            print("No Virtual Machines to stop for workout %s" % workout_id)
        return True
    except():
        print("Error in starting VM for %s" % workout_id)
        return False