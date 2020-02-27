import googleapiclient.discovery
from google.cloud import datastore

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
dns_suffix = ".cybergym-eac-ualr.org"
project = 'ualr-cybersecurity'
dnszone = 'cybergym-public'

class WORKOUT_BOUNDS():
    MAX_RUN_HOURS = 10

c