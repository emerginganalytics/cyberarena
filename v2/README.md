# Deploying Verison 2 of the Cyber Arena
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