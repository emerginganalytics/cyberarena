# Authentication Setup
1. Navigate to the Identify Platform at https://console.cloud.google.com/marketplace/product/google-cloud-platform/customer-identity and enable the API. 
2. Click to create a new Identity Provider and select Email/Password. The defaults are fine to use. You may also set up other providers as needed
3. Configure the OAuth consent screen at https://console.cloud.google.com/apis/credentials/consent. When setting this screen up, make sure to include the domain for this project in the authorized domains.
4. Create API credentials to use in the main application by going to https://console.cloud.google.com/apis/credentials and clicking on Create Credentials and selecting API key. Copy this API key. You will need to use this when deploying the application.
