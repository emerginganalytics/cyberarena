import argparse
import os
import sys
import time
import googleapiclient.discovery
import calendar
from six.moves import input
from googleapiclient.errors import HttpError

compute = googleapiclient.discovery.build('compute', 'v1')


# -------------------- BUILD WORKOUT FLAG STARTUP --------------------------

def build_flag_startup(flag_os, name, flag):
    # Takes OS type and flag and generates a startup based on OS.
    # Files are created and stored to bucket
    # "gs://ualr-cybersecurity-bucket/startup-scripts/flags/" using machine name as
    # identifier for flag file
    from google.cloud import storage as gcs

    client = gcs.Client()
    flag_bucket = client.get_bucket('ualr-cybersecurity-bucket')
    script = ''

    if flag_os == 'linux':
        script  = '#!/bin/bash\n'
        script += 'cd /usr/local/share/planted/\n' # 'sudo mkdir /usr/local/share/planted/ && cd /usr/local/share/planted\n'
        script += 'sudo echo {} > flag.txt'.format(flag)

        file_name = name + '.sh'
        bucket_file = flag_bucket.blob('startup-scripts/flags/' + file_name)  # + something.sh

    elif flag_os == 'windows':
        flag_dir = 'C:\\Program Files\\Google\\Compute Engine\\planted'
        script  = '@echo off\n'
        script += 'mkdir {} && cd {}\n'.format(flag_dir, flag_dir)
        script += 'echo {} > flag.txt' .format(flag)

        file_name = name + '.bat'
        bucket_file = flag_bucket.blob('startup-scripts/flags/' + file_name)  # + something.sh

    bucket_file.upload_from_string(script)
    # return file_name
    return script

# temp fix: instances don't have permissions to buckets. Alt is to just return the script instead of bucket url.
# works as long as script isn't too long

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
# ** Function now requires two more arguments, flag_container and flag_startup. The first is the machine name where the
# **  flag is stored. flag_startup is the result of running build_flag_startup()

def create_instance_custom_image(compute, project, zone, name, flag_container, flag_startup, flag,
                                 bucket, custom_image, internal_IP,
                                 network_name, subnet_name, accessConfigs=None, tags=None):
    # Get the latest Debian Jessie image.
    
    image_response = compute.images().get(project='ualr-cybersecurity', image=custom_image).execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone

    # add custom metadata only if machine == flag_container
    if name == flag_container:

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
                    'subnetwork': 'regions/us-central1/subnetworks/' + str(subnet_name),
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
                    {
                        'key': 'startup-script',
                        'value': flag_startup
                    }
                ]

            }
        }
    else:
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
                    'subnetwork': 'regions/us-central1/subnetworks/' + str(subnet_name),
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

def build_dos_vm(network, subnet, workout_id):
    
    # create a network for this workout
    # TO DO

    print("build dos network : {}".format(network))

    # create the vm for the dos workout and assign them to the previous network
    list_images_to_create = ['image-labentry','image-cybergym-dvwalab','image-promise-attacker']
    list_internal_ip = ['10.1.1.10', '10.1.1.3', '10.1.1.4']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, None, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['http-server','https-server']}, None, {'items': ['http-server','https-server']}]

    # we store each response in this list --> specially to retrieve ext IP of the labentry
    list_response = []

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-dos-{}'
                                     .format(workout_id, image[6:]), 'ualr-cybersecurity', image,
                                     int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('{}-dos-{}'.format(workout_id, image[6:])))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-dos-labentry'.format(workout_id))
    response = request.execute()

    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MQBjAG15c3Fs"
    
    return guaca_redirection

# -------------------- BUILD XSS WORKOUT --------------------------


def build_xss_vm(network, subnet, workout_id):

    list_images_to_create = ['image-cybergym-dvwalab', 'image-labentry']
    list_internal_ip = ['10.1.1.253', '10.1.1.10']
    list_ext_ip = [None, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['guac-server']}, {'items': ['http-server', 'https-server', 'guac-server']}]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a',
                                     '{}-xss-{}'.format(workout_id, image[6:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-xss-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MgBjAG15c3Fs"

    # dvwa_redirection = "http://" + ext_IP + "/DVWA"

    return guaca_redirection

# -------------------- BUILD CYBERATTACK WORKOUT --------------------------


def build_cyberattack_vm(network, subnet, workout_id):
    list_images_to_create = ['image-labentry', 'image-promise-victim-win2012']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['http-server','https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-attacker-{}'.format(workout_id, image[6:]),
                            'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('{}-attacker-{}'.format(workout_id, image[6:])))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    print("ext ip from :",'{}-attacker-labentry'.format(workout_id))
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-attacker-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MgBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD SPOOF WORKOUT --------------------------

def build_spoof_vm(network, subnet, workout_id):

    list_images_to_create = ['image-labentry', 'image-windows', 'image-promise-attacker']
    list_internal_ip = ['10.1.1.10', '10.1.1.5', '10.1.1.9']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, None, None]
    list_tags = [{'items': ['http-server', 'https-server']}, None, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-spoof-{}'.format(workout_id, image[6:]),
                            'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('{}-attacker-{}'.format(workout_id, image[6:])))

    # we want to retrieve the external IP for the labentry VM
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-spoof-labentry'.format(workout_id))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD HIDDEN NODE WORKOUT --------------------------

def build_hiddennode_vm(network, subnet, workout_id, flag):

    list_images_to_create = ['image-labentry',
                             'image-cybergym-dvwalab', 'ce-linux-boot-image-002',  'ce-windows-boot-image-002']
    list_internal_ip = ['10.1.1.10', '10.1.1.253', '10.1.1.111', '10.1.1.115', '10.1.1.25']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None, None, None, None]
    list_tags = [{'items': ['http-server', 'https-server', 'guac-server', 'attacker', 'vnc-server']}, None, None, None, None]

    # specify which instance you want to store the flag on: [called in metadata]
    flag_location = 'image-cybergym-dvwalab'
    flag_container = '{}-hiddennode-{}'.format(workout_id, flag_location[6:])

    # build the startup script
    flag_startup = build_flag_startup('linux', flag_container, flag)

    # building instances
    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a',
                                     '{}-hiddennode-{}'.format(workout_id, image[6:]), flag_container, flag_startup,
                                     flag, 'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)
        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-hiddennode-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# -------------------- BUILD IDS NODE WORKOUT --------------------------

def build_ids_vm(network, subnet, workout_id):

    list_images_to_create = ['image-labentry',
                             'image-cybergym-dvwalab']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None]
    list_tags = [{'items': ['http-server', 'https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-ids-{}'.format(workout_id, image),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-ids-image-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# ----------------------- BUILD PHISHING WORKOUT ---------------------------


def build_phishing_vm(network, subnet, workout_id):
    list_images_to_create = ['image-labentry', 'image-promise-vnc']
    list_internal_ip = ['10.1.1.18', '10.1.1.20']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['attacker', 'vnc-server', 'guac-server', 'http-server', 'https-server']},
                 {'items': ['attacker', 'vnc-server', 'guac-server', 'http-server', 'https-server']}]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-phishing-{}'.format(workout_id, image),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-phishing-image-labentry'.format(workout_id))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
                        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection


# ----------------------- BUILD FIREWALL WORKOUT ---------------------------


def build_theharbor_vm(network, subnet, workout_id):
    list_images_to_create = ['image-promise-vnc', 'image-labentry']
    list_internal_ip = ['10.128.0.20', '10.128.0.18']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'}, None]
    list_tags = [{'items': ['http_server', 'https-server', 'attacker', 'vnc-server', 'guac-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity', 'us-central1-a', '{}-theharbor-{}'.format(workout_id, image),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format(image))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-theharbor-image-labentry'.format(workout_id))

    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + \
                        ":8080/guacamole/#/client/MQBjAG15c3Fs"

    return guaca_redirection

# ----------------------------------- Hash My Files Workout ---------------------------------------------------


def build_hashmyfiles_vm(network, subnet, workout_id):

    list_images_to_create = ['image-labentry', 'image-promise-win-2016']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    list_tags = [{'items': ['http-server','https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity',
                                     'us-central1-a', '{}-hashmyfiles-{}'.format(workout_id, image[6:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('{}-hashmyfiles-{}'.format(image[6:], workout_id)))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    print("ext ip from :", '{}-hashmyfiles-labentry'.format(workout_id))
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-hashmyfiles-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/MgBjAG15c3Fs"

    return guaca_redirection


# ----------------------------------- Mobile Forensics Workout ---------------------------------------------------


def build_mobileforensics_vm(network, subnet, workout_id):

    list_images_to_create = ['image-labentry', 'image-cybergym-forensics-workstation']
    list_internal_ip = ['10.1.1.10', '10.1.1.11']
    list_ext_ip = [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}, None]
    list_tags = [{'items': ['http-server','https-server']}, None]

    for i in range(len(list_images_to_create)):
        image = list_images_to_create[i]
        int_IP = list_internal_ip[i]
        ext_IP = list_ext_ip[i]
        tags = list_tags[i]

        create_instance_custom_image(compute, 'ualr-cybersecurity',
                                     'us-central1-a', '{}-mobileforensics-{}'.format(workout_id, image[6:]),
                                     'ualr-cybersecurity', image, int_IP, network, subnet, ext_IP, tags)

        print("{} created".format('{}-mobileforensics-{}'.format(image[6:], workout_id)))

    # we want to retrieve the external IP for the labentry VM
    time.sleep(5)
    print("ext ip from :", '{}-mobileforensics-labentry'.format(workout_id))
    request = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                      instance='{}-mobileforensics-labentry'.format(workout_id))
    response = request.execute()
    ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    guaca_redirection = "http://" + ext_IP + ":8080/guacamole/#/client/NwBjAG15c3Fs"

    return guaca_redirection