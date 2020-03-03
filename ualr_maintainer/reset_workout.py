import googleapiclient.discovery
from globals import ds_client, project, compute, dnszone, workout_globals, dns_suffix
import time
import calendar

# Global variables for this function
expired_workout = []
zone = 'us-central1-a'
region = 'us-central1'

# Create a new DNS record for the server and add the information to the datastore for later management
def register_workout_update(project, dnszone, workout_id, old_ip, new_ip):
    service = googleapiclient.discovery.build('dns', 'v1')

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    change_body = {
        "deletions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": workout_id + dns_suffix + ".",
                "rrdatas": [old_ip],
                "type": "A",
                "ttl": 30
            }
        ],
        "additions": [
        {
            "kind": "dns#resourceRecordSet",
            "name": workout_id + dns_suffix + ".",
            "rrdatas": [new_ip],
            "type": "A",
            "ttl": 30
        }
    ]}

    request = service.changes().create(project=project, managedZone=dnszone, body=change_body)
    response = request.execute()


    workout["external_ip"] = new_ip
    workout['running'] = True
    workout['start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(workout)



def reset_workout(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    try:
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().reset(project=project, zone=zone, instance=vm_instance["name"]).execute()
                workout_globals.extended_wait(project, zone, response["id"])

                started_vm = compute.instances().get(project=project, zone=zone, instance=vm_instance["name"]).execute()
                if 'accessConfigs' in started_vm['networkInterfaces'][0]:
                    if 'natIP' in started_vm['networkInterfaces'][0]['accessConfigs'][0]:
                        tags = started_vm['tags']
                        if tags:
                            for item in tags['items']:
                                if item == 'labentry':
                                    ip_address = started_vm['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                                    register_workout_update(project, dnszone, workout_id, workout["external_ip"], ip_address)
            print("Finished resetting %s" % workout_id)
        return True
    except():
        print("Error in resetting VM for %s" % workout_id)
        return False
