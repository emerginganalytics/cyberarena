# Deploying Version 2 of the Cyber Arena
## Prerequisites
1. Create a new Google Cloud Project: https://console.cloud.google.com/
2. Install the Google Cloud SDK: https://cloud.google.com/sdk/install
3. Create a service account with owner access and download a local key here: https://console.cloud.google.com/iam-admin/serviceaccounts.
    You will need to save this (e.g. C:\Users\<username>\.gcp\cyberarena.json). This key will be used for running the setup.
4. Set up the Identity Platform service and obtain the API key as follows:
    1. Navigate to the Identify Platform at 
        https://console.cloud.google.com/marketplace/product/google-cloud-platform/customer-identity and enable the API.
    2. Click to create a new Identity Provider and select Email/Password. The defaults are fine to use. 
        You may also set up other providers as needed
    3. Configure the OAuth consent screen at https://console.cloud.google.com/apis/credentials/consent. 
        When setting this screen up, make sure to include the domain for this project in the authorized domains.
    4. Create API credentials to use in the main application by going to 
        https://console.cloud.google.com/apis/credentials and clicking on Create Credentials and selecting API key. 
        Copy this API key. You will need to use this when deploying the application.
5. Enable the DNS service and create a new managed domain (e.g. mycyberarena.com). **The zone must be named cybergym-public.**
6. Increase quotas according the following recommendations based on Max Concurrent Build (MCB)
    1. Compute Engine API (Subnetworks) - MCB * 2
    2. Compute Engine API (Networks) - MCB * 1
    3. Compute Engine API (Firewall Rules) - MCB * 3
    4. Compute Engine API (Routes) - MCB * 2
    5. Compute Engine API (In-Use IP Addresses) - MCB * 1
    6. Compute Engine API (CPUs) - MCB * 3
    7. Cloud Build API (Concurrent Builds) - 50
7. Install the PyCharm IDE here: https://www.jetbrains.com/pycharm/ - You will use this to run setup.py as described in the deployment section below.

## Deployment
Create a new project in PyCharm at the root of this directory, and then set `build_files`, `cloud_functions`, and `main_app` directories as _sources root_ in PyCharm (i.e., right click --> mark directory --> sources root). Open `setup.py` and create a new configuration to run `setup.py`. This will ensure the sources directories are easily recognized. Follow the instructions in the prompt. You can also use `setup.py` for synchronizing cloud
resources and running updates.

### Bulk Deployment
Multiple projects can be updated by running bulk deployment. To do so, you need to provide a settings file named 
`.bulk_settings.yaml` in the same directory as `setup.py`. This file should be included in .gitignore. The yaml specification
for this file should be:
```yaml
# Include the list of functions you are wanting to bulk deploy. They may be any of the following
deploy_functions:
  - CLOUD_FUNCTION
  - MAIN_APP
  - BUILD_SPECS
  - ENV
# Include the list of projects to deploy. The list should include the project name and filename of the credential
gcp_projects:
  - name: 'sample-project'
    credential: 'C:\Users\jdoe\.gcp\sample-project.json'
```

## Creating Your Own Specifications
To create your own labs for students. You need the following:
1. Clone this repo and make sure you have all the prerequisites from above to run setup.py on your laptop.
2. Run setup.py and choose the option to _Synchronize and Encrypt/Decrypt Build Specifications, Instructions, and Compute Images_. This will sync the plaintext specifications under `v2/build_files/specs/plaintext`. Contact an administrator for the password. 
3. Create new compute servers in the Google Project. Configure the server the way you want students to see it, and then stop the server.
4. Create a new specification under the plaintext specs folder. The easiest way to do so is probably copying an existing one, but you can see the full specification here: `v2/main_app/main_app_utilities/infrastructure_as_code/schema.py`
5. Run setup.py again and choose _Prepare a single specification for deployment_. This will automatically prepare servers in your project for use in the lab, and upload the specification to the cloud bucket for use in your application.

## Architecture
The Cyber Arena includes two main application. First, the _main_app_ provides the web application for instructors and students
to interact with the configured labs. This runs as a cloud run app with Firebase authentication and provides entry into
the cybersecurity labs through an Apache Guacamole proxy server. Secondly, the _cloud_functions_ provide somewhat of
a backend to manage the cybersecurity labs efficiently.

### Cloud Functions
The cloud functions are container application similar to the _main_app_. Functions are initiated through a series of
PubSub messages. The PubSub messages come either through the web application or a cloud scheduler. A function 
responding to PubSub messages is like an API endpoint, and we may switch the architecture to use APIs in the future 
when cloud function APIs are better supported.

As of this writing, we have a single cloud function that accepts many types of calls. The cloud function is 
`cyber_arena_cloud_function` in `main.py`. Having a single function helps with deployment and consistency. The 
function subscribes to a _cyber-arena_ topic and then passes off the function request to one of its handlers. All
data needed for the handlers is passed through to its final performing function. The handlers include:
1. **Build Handler** - Responds to request to build a lab component (e.g. class, workspace, server, etc.)
2. **Control Handler** - Responds to any user-initiated interaction from the main-app
3. **Maintenance Handler** - Responds to cloud scheduler PubSub messages

#### Concurrent Operations in Cloud Functions
Several operations require a lengthy waiting period after sending a job to the cloud. To prevent long wait times, 
the cloud function will recursively call itself when encountering a cloud job by sending additional PubSub messages.
For example, when building a lab, the initial routine will send separate PubSub messages for all of its servers.
Then, each server gets built concurrently. Also, when deleting expired workspaces, each workspace deletion is
called asynchronously and each workspaces calls its server deletion asynchronously. 

### Maintenance
Cloud maintenance occurs every 15 minutes by the cloud scheduler simply sending a blank message to the _cyber-arena_ 
PubSub topic. The maintenance handler than queries the current time and runs its daily, hourly, and quarter-hourly
tasks based on the time. The maintenance tasks include the following:
1. **Daily** - Stop any running servers
2. **Hourly** - None at this time
3. **Quarter-Hourly**
   1. Turns off any labs having expired their maximum run time.
   2. Deletes any labs having expired their lifetime
   3. Attempts to fix any labs which may be in a failed state.
