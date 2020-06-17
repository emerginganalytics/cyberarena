import googleapiclient.discovery
from common.globals import ds_client, dns_suffix, project, dnszone

# Create a new DNS record for the server and
def add_dns_record(build_id, ip_address):
    service = googleapiclient.discovery.build('dns', 'v1')

    change_body = {"additions": [
        {
            "kind": "dns#resourceRecordSet",
            "name": build_id + dns_suffix + ".",
            "rrdatas": [ip_address],
            "type": "A",
            "ttl": 30
        }
    ]}

    request = service.changes().create(project=project, managedZone=dnszone, body=change_body)
    response = request.execute()


# Add the information to the datastore for later management.
# We are deprecating this as we build out the guacamole automation.
def register_workout_server(workout_id, server, guac_path):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["servers"].append({"server": server, "guac_path": guac_path})
    ds_client.put(workout)
