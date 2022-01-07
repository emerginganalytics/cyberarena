# Cyber Gym Command Line Scripts
This directory contains scripts for maintaining the Cyber Gym. These may have not been included in the admin application.

## Running Locally
1. Before running these scripts locally, make sure to modify or create a PYTHONPATH environment variable to include cybergym/cloud-functions.
2. Also, in PyCharm, set the cloud-functions directory as Sources Root.
3. You will need an API key for the Cyber Gym project you are working on. You can set the API key in the environment variable: GOOGLE_APPLICATION_CREDENTIALS

## Creating Scripts
To create maintenance scripts, use the click library. Make sure to comment your code and include help tags for any flags.