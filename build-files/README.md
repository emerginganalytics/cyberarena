# Deploying the Cyber Arena
## Prerequisites
Before running the setup scripts, perform the following steps to prepare your cloud project.
1. Create a new Google Cloud Project: https://console.cloud.google.com/
2. Install the Google Cloud SDK if you have not already done so: https://cloud.google.com/sdk/install
3. Register a domain to use for the Cyber Arena project: https://console.cloud.google.com/net-services/domains/registrations/create
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
5. Increase quotas according the following recommendations based on Max Concurrent Build (MCB)
    1. Compute Engine API (Subnetworks) - MCB * 2
    2. Compute Engine API (Networks) - MCB * 1
    3. Compute Engine API (Firewall Rules) - MCB * 3
    4. Compute Engine API (Routes) - MCB * 2
    5. Compute Engine API (In-Use IP Addresses) - MCB * 1
    6. Compute Engine API (CPUs) - MCB * 3
    7. Cloud Build API (Concurrent Builds) - 50

## Deployment
Run the python script `build-update-scripts/build-cyber-gym.python` to deploy the Cyber Arena to your new cloud project. 
The script walks you through the following steps:
1. Enables all of the necessary cloud APIs
2. Creates a new cloud service account
3. Creates all of the pubsub topics needed for periodic maintenance
4. Creates the storage bucket for Cyber Arena build specifications
5. Creates the environment variables that point the Cyber Arena application to your specific instance
6. Optionally creates a database for workouts needing a SQL database
7. Deploys all of the cloud functions necessary to build and maintain workouts in the Cyber Arena. NOTE: 
This step may take several minutes.
8. Creates the schedules to periodically deploy the cloud functions
9. Creates the main applications and any container applications.

## Applying Updates
It may be necessary to update the Cyber Arena deployments from time to time to fix issues or apply new functionality.
Run `build-update-scripts/update-cyber-gym.python` to perform update functions. This script will prompt you
for the type of updates you wish to perform.

## Patching
Patch scripts may be provided to migrate between major versions. This will assist in only adding new functionality.

## Workout Deployments
Workout deployment packages are provided in the [Workout Deployment Packages Folder](build-update-scripts/workout-deployment-packages).
This folder contains several deployment packages to assist in ensuring all necessary resources are uploaded to the
Cyber Arena before building workouts. A deployment package contains a listing of workouts that include the unit name
and a set of workout specifications associated with the unit.

## Child Deployments
Currently, Google restricts most cloud projects to a maximum build size of 300 workouts. However, the Cyber Arena
can span across multiple Google projects to allow horizontal scaling while still maintaining a single, coherent
Cyber Arena deployment. To create new child projects, run the `build-update-scripts/create_update_child_gym.python`
script.
