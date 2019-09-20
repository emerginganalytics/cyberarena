import argparse
import os
import time
import googleapiclient.discovery
import calendar
from six.moves import input
from googleapiclient.errors import HttpError

compute = googleapiclient.discovery.build('compute', 'v1')


# -------------------- TEST GOOGLE API AUTHENTICATION --------------------------

def implicit():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())

    for buck in buckets:
        print(buck.name)
        create_instance_ubuntu(compute, 'ualr-cybersecurity', 'us-central1-a', 'YOYO', buck.name)

# implicit()

# try:
#     create_dos_workout(compute, 'ualr-cybersecurity', 'us-central1-a', 'new-test-build-dvwa', 'ualr-cybersecurity-bucket')
# except:
#     print('error')


# ------------------------ LIST EXISTING VM ------------------------------

# list all existing instances
def list_instances(compute, project, zone):

    # store the vm name into a list
    list_vm = []

    result = compute.instances().list(project=project, zone=zone).execute()

    try:
        for vm_instance in result['items']:
            list_vm.append(vm_instance)
    except():
        print("No VM found")

    print('-------------- VM list retrieved --------------')  
    print(list_vm)
    # return list_vm
    #return result['items'] if 'items' in result else None

# list_instances(compute, 'ualr-cybersecurity', 'us-central1-a')


# -------------------- TEST REGULAR VM INSTANCIATION --------------------------

def create_instance_ubuntu(compute, project, zone, name, bucket):

    # Get image of the OS we want ot create, list available here :
    # https://cloud.google.com/compute/docs/images
    image_response = compute.images().getFromFamily(project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine --> specify the shell script we want to use
    # We can create as many shell script as we want different VM configurations --> must be specified in the metadata below
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script_custom = open(os.path.join(os.path.dirname(__file__), 'startup-custom-script.sh'), 'r').read()

    # VM general config 
    config = {
        'name': name,
        'machineType': machine_type,

        # allow http and https server with tags
        'tags': {
            'items': [
                'http-server','https-server'
            ]
        },

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script_custom
            }, 
            {
                'key': 'bucket',
                'value': bucket
            }]
        },
    }

# create_instance_ubuntu(compute, 'ualr-cybersecurity', 'us-central1-a', 'YOYO', 'dvwa-test-gaetan')


# -------------------- CREATE CUSTOM IMAGE --------------------------

def create_instance_custom_image(compute, project, zone, name, 
                                    bucket, custom_image, internal_IP,
                                    network_name, subnet_name, accessConfigs=None, tags=None):
    # Get the latest Debian Jessie image.
    
    image_response = compute.images().get(project='ualr-cybersecurity', image=custom_image).execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone

    config = {
        'name': name,
        'machineType': machine_type,

        # allow http and https server with tags
        'tags': tags,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.

        'networkInterfaces': [
            {
                'network': 'projects/ualr-cybersecurity/global/networks/' + network_name,
                'subnetwork': 'regions/us-central1/subnetworks/' + subnet_name,
                'networkIP': internal_IP,
                'accessConfigs': [
                    accessConfigs
                ]
            }
        ],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [
             {
                'key': 'bucket',
                'value': bucket
             },
            
            
            ]
        }
    }

    compute.instances().insert(project=project, zone=zone, body=config).execute()
    return 'Done'


# -------------------- BUILD DOS WORKOUT --------------------------

def build_dos_vm(network, subnet, ts):
    
    # create a network for this workout
    # TO DO

    print("build dos network : {}".format(network))

    # create the vm for the dos workout and assigne them to the previous network
    list_images_to_create = ['image-labentry','image-promise-dvwalab','image-promise-attacker']
    list_internal_ip = ['10.1.1.10', '10.1.1.3', '10.1.1.4']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, None, None]
    list_tags = [{'items': ['http-server','https-server']}, None, None]

    # we store each response in this list --> specially to retrieve ext IP of the labentry
    list_response = []

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', 'dos-{}-{}'.format(image[6:], network[-9:]),
                                    'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('dos-{}-{}'.format(image[6:], network[-9:])))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='dos-labentry-{}'.format(network[-9:]))
    response = request.execute()

    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MQBjAG15c3Fs"
    
    return guaca_redirection


# -------------------- BUILD CYBERATTACK WORKOUT --------------------------

def build_cyberattack_vm(network, subnet, ts):

    list_images_to_create = ['image-labentry', 'image-promise-victim-win2012']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['http-server','https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', 'attacker-{}-{}'.format(image[6:], network[-9:]),
                            'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('attacker-{}-{}'.format(image[6:], network[-9:])))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    print("ext ip from :",'attacker-labentry-{}'.format(network[-9:]))
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='attacker-labentry-{}'.format(network[-9:]))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MgBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD SPOOF WORKOUT --------------------------

def build_spoof_vm(network, subnet, ts):

    list_images_to_create = ['image-labentry', 'image-windows', 'image-promise-attacker']
    list_internal_ip = ['10.1.1.10', '10.1.1.5', '10.1.1.9']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, None, None]
    list_tags = [{'items': ['http-server', 'https-server']}, None, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', 'spoof-{}-{}'.format(image[6:], network[-9:]),
                            'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)


        print("{} created".format('attacker-{}-{}'.format(image[6:], network[-9:])))

    # we want to retrieve the external IP for the labentry VM
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='spoof-labentry-{}'.format(network[-9:]))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD HIDDEN NODE WORKOUT --------------------------

def build_hiddennode_vm(network, subnet, ts):

    list_images_to_create = ['image-labentry',
                             'image-promise-dvwalab', 'ce-linux-boot-image-002']
    list_internal_ip = ['10.1.1.10', '10.1.1.253', '10.1.1.111']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None, None]
    list_tags = [{'items': ['http-server', 'https-server']}, None, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', 'hiddennode-{}-{}'.format(image[6:], network[-9:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='hiddennode-labentry-{}'.format(network[-9:]))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD IDS NODE WORKOUT --------------------------

def build_ids_vm(network, subnet, ts):

    list_images_to_create = ['image-labentry',
                             'image-promise-dvwalab']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None]
    list_tags = [{'items': ['http-server', 'https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', 'ids-{}-{}'.format(image, network[-9:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='ids-image-labentry-{}'.format(network[-9:]))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# ----------------------- BUILD PHISHING WORKOUT ---------------------------


def build_phishing_vm(network, subnet, ts):
    list_images_to_create = ['image-promise-vnc', 'image-labentry']
    list_interal_ip = ['10.128.0.20', '10.128.0.18']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None]
    list_tags = [{'items': ['http_server', 'https-server', 'attacker', 'vnc-server', 'guac-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_interal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central-a', 'phishing-{}-{}'.format(image, network[-9:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central-a',
                                      instance='phishing-image-labentry-{}'.format(network[-9:]))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
                        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# ----------------------- BUILD FIREWALL WORKOUT ---------------------------


def build_theharbor_vm(network, subnet, ts):
    list_images_to_create = ['image-promise-vnc-final', 'image-labentry']
    list_interal_ip = ['10.128.0.20', '10.128.0.18']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None]
    list_tags = [{'items': ['http_server', 'https-server', 'attacker', 'vnc-server', 'guac-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_interal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central-a', 'theharbor-{}-{}'.format(image, network[-9:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central-a',
                                      instance='theharbor-image-labentry-{}'.format(network[-9:]))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
                        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection
