# Cyber Gym Command Line Scripts
This directory contains scripts for maintaining deployments and automating maintenanc tasks in the Cyber Arena.

## Running Locally
1. Before running these scripts locally, make sure to modify or create a PYTHONPATH environment variable to include 
cyberarena/admin_scripts. If you run these through PyCharm, there's no need to manually set the PYTHONPATH variable.
2. Also, in PyCharm, set the cloud-functions and main directories as Sources Root.
3. You will need an API key for the Cyber Gym project you are working on. You can set the API key in the environment 
variable: GOOGLE_APPLICATION_CREDENTIALS

## Creating Scripts
To create maintenance scripts, add a new python file and use the argparse library to manage arguments. 
Make sure to comment your code and include help tags for any flags.