import googleapiclient.discovery
from google.cloud import datastore

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
dns_suffix = ".acactb.com"
project = 'acapte'
dnszone = 'aca-bootcamp-public'