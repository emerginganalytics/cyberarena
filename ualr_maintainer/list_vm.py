import googleapiclient.discovery

list_vm = []
compute = googleapiclient.discovery.build('compute', 'v1')

# list all existing instances
def list_instances(project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()

    # print(result['items'][0]['name'])

    try:
        for vm_instance in result['items']:
            list_vm.append(vm_instance)
    except():
        print("No VM found")

    return list_vm

# list_instances('ualr-cybersecurity', 'us-central1-a')

