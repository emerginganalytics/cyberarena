# UALR Cyber Gym

This repository contains the scripts needed for various labs in the UA Little Rock Online Cybersecurity Curriculum.

## Setup
1. Download repository from BitBucket
2. Install Python 3.7 or above from python.org
3. Download and install Google SDK
4. In the cloud console, go to IAM & Admin > Service Accounts and select the Builder account. Add a new key under this account and download it. (If the account is at the maximum number of keys, delete the oldest key and create a new one.)
5. From either the system command line or from the terminal inside Pycharm run the command 'python -m pip install --user virtualenv' then use 'pip install virtualenv'
6. Create a new folder for your environment or create a new project folder in Pycharm
7. Activate the environment by running 'python -m virtualenv <environment location>' and '.\Scripts\activate' (this is for windows, MAC and Linux will be slightly different, check the attached video)
8. Install requirements from the repository using 'pip install -r <repository location>\requirements.txt' (This may take a bit to install everything)
9. To disable the environment, repeat step 7 using '.\Scripts\deactivate' instead. When working on the project just reactivate as needed.
Useful Resources:

Video on setting up and activating virtualenv (Primarily MAC and Linux)- 
	https://youtu.be/N5vscPTWKOk
    
Helpful Guides for setting up on Windows- 
	https://programwithus.com/learn-to-code/Pip-and-virtualenv-on-Windows/
	https://stackoverflow.com/questions/35950740/virtualenv-is-not-recognized-as-an-internal-or-external-command-operable-prog