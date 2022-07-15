# Deploying Version 2 of the Cyber Arena
## Prerequisites
1. Create a new Google Cloud Project: https://console.cloud.google.com/
2. Install the Google Cloud SDK: https://cloud.google.com/sdk/install
3. Set up the Identity Platform service and obtain the API key as follows:
    1. Navigate to the Identify Platform at 
        https://console.cloud.google.com/marketplace/product/google-cloud-platform/customer-identity and enable the API.
    2. Click to create a new Identity Provider and select Email/Password. The defaults are fine to use. 
        You may also set up other providers as needed
    3. Configure the OAuth consent screen at https://console.cloud.google.com/apis/credentials/consent. 
        When setting this screen up, make sure to include the domain for this project in the authorized domains.
    4. Create API credentials to use in the main application by going to 
        https://console.cloud.google.com/apis/credentials and clicking on Create Credentials and selecting API key. 
        Copy this API key. You will need to use this when deploying the application.
4. Enable the DNS service and create a new managed domain (e.g. mycyberarena.com)
5. Increase quotas according the following recommendations based on Max Concurrent Build (MCB)
    1. Compute Engine API (Subnetworks) - MCB * 2
    2. Compute Engine API (Networks) - MCB * 1
    3. Compute Engine API (Firewall Rules) - MCB * 3
    4. Compute Engine API (Routes) - MCB * 2
    5. Compute Engine API (In-Use IP Addresses) - MCB * 1
    6. Compute Engine API (CPUs) - MCB * 3
    7. Cloud Build API (Concurrent Builds) - 50

## Deployment
Run `python setup.py` and follow the instructions in the prompt. You can also use `setup.py` for synchronizing cloud
resources and running updates.

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
