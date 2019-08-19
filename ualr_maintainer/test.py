import argparse
import os
import time
import googleapiclient.discovery
import calendar
from six.moves import input
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date

compute = googleapiclient.discovery.build('compute', 'v1')

def isReadyToDelete(created_date):

    now = datetime.now()
    print(now)

    intance_creation_date = datetime.strptime(created_date[:19], '%Y-%m-%dT%H:%M:%S')
    print(intance_creation_date)

    delta = now - intance_creation_date
    print (delta.days)

# delete all expired instances
def del_expired_instances(compute, project, zone):

    # store the vm name into a list
    list_vm = []

    result = compute.instances().list(project=project, zone=zone).execute()

    try:
        for vm_instance in result['items']:
            list_vm.append(vm_instance)
    except():
        print("No VM found")

    # test only the instances created for t workout --> contain "team" inside their names
    for instance in list_vm:
        if "team" in instance['name']:
            print(instance['name'])
            print("creation date of the vm :", instance['creationTimestamp'])
            isReadyToDelete(instance['creationTimestamp'])


del_expired_instances(compute, 'ualr-cybersecurity', 'us-central1-a')
