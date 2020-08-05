import googleapiclient.discovery

project = 'FILLIN'
dnszone = 'FILLIN'

service = googleapiclient.discovery.build('dns', 'v1')

response = service.resourceRecordSets().list(project=project, managedZone=dnszone).execute()
delete_records = []
for record in response['rrsets']:
    if record['type'] == 'A':
        delete_records.append(record)
change_body = {
    "deletions": delete_records,
    "additions": []}
service.changes().create(project=project, managedZone=dnszone, body=change_body).execute()
