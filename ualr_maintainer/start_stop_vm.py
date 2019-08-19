import googleapiclient.discovery

compute = googleapiclient.discovery.build('compute', 'v1')

project = 'ualr-cybersecurity'
region = 'us-central1-a'

def stop_vm(instance):

    instance = instance

    request = compute.instances().stop(project=project, zone=region, instance=instance)
    response = request.execute()


def start_vm(instance):

    instance = instance

    request = compute.instances().start(project=project, zone=region, instance=instance)
    response = request.execute()

