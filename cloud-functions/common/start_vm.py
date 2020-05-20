#
# This script is intended to be copied into the landing page application for the button click when
# resuming a workout which has previously been stopped.
#
import googleapiclient.discovery
from common.globals import ds_client, project, compute, dnszone, dns_suffix
import time
import calendar
from googleapiclient.errors import HttpError

# Global variables for this function
expired_workout = []
zone = 'us-central1-a'
region = 'us-central1'


# Create a new DNS record for the server and add the information to the datastore for later management
def register_workout_update(project, dnszone, workout_id, new_ip):
    service = googleapiclient.discovery.build('dns', 'v1')

    # First, get the existing workout DNS
    response = service.resourceRecordSets().list(project=project, managedZone=dnszone,
                                              name=workout_id + dns_suffix + ".").execute()
    existing_rrset = response['rrsets']
    change_body = {
        "deletions": existing_rrset,
        "additions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": workout_id + dns_suffix + ".",
                "rrdatas": [new_ip],
                "type": "A",
                "ttl": 30
            }
    ]}

    # Try first to perform the DNS change, but in case the DNS did not previously exist, try again without the deletion change.
    try:
        request = service.changes().create(project=project, managedZone=dnszone, body=change_body).execute()
    except HttpError:
        try:
            del change_body["deletions"]
            request = service.changes().create(project=project, managedZone=dnszone, body=change_body).execute()
        except HttpError:
            # Finally, it may be the DNS has already been successfully updated, in which case
            # the API call will throw an error. We ignore this case.
            pass

    # Now update the parameters in the workout object
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["external_ip"] = new_ip

    ds_client.put(workout)


def start_workout(workout_id):
    print("Starting workout %s" % workout_id)
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout['running'] = True
    workout['start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(workout)

    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    try:
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().start(project=project, zone=zone, instance=vm_instance["name"]).execute()
                workout_globals.extended_wait(project, zone, response["id"])

                started_vm = compute.instances().get(project=project, zone=zone, instance=vm_instance["name"]).execute()
                if 'accessConfigs' in started_vm['networkInterfaces'][0]:
                    if 'natIP' in started_vm['networkInterfaces'][0]['accessConfigs'][0]:
                        tags = started_vm['tags']
                        if tags:
                            for item in tags['items']:
                                if item == 'labentry':
                                    ip_address = started_vm['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                                    register_workout_update(project, dnszone, workout_id, ip_address)
            time.sleep(30)
            print("Finished starting %s" % workout_id)
        return True
    except():
        print("Error in starting VM for %s" % workout_id)
        return False
