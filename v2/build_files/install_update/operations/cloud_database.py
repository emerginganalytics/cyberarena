import subprocess
import random
import string
from googleapiclient import discovery

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CloudDatabase:
    """
    Creates the cloud database.
    TODO: Automatically set the IP address of the sql database
    """
    CREATE_DATABASE = "gcloud sql instances create cybergym --tier=db-g1-small --region=us-central"
    CREATE_USER = "gcloud sql users set-password root --host=% --instance cybergym --password {password}"
    CREATE_INSTANCE = "gcloud sql databases create cybergym --instance=cybergym"
    OPEN_ACCESS = "gcloud sql instances patch cybergym --authorized-networks=0.0.0.0/0"
    SET_VARIABLE = "gcloud beta runtime-config configs variables set \"{variable}\" \"{value}\" --config-name \"cybergym\""

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()

    def deploy(self):
        print(f"Beginning to create database...")
        command = self.CREATE_DATABASE
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error creating database!")
            return False
        print(f"Creating the root user...")
        sql_password = ''.join(random.choice(string.printable) for j in range(25))
        command = self.SET_VARIABLE.format(variable="sql_password", value=sql_password)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        command = self.CREATE_USER.format(password=sql_password)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error creating root user")
            return False
        print(f"Creating the cybergym database...")
        command = self.CREATE_INSTANCE
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error creating the database")
            return False
        print(f"Opening access to the database...")
        command = self.OPEN_ACCESS
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error opening access to the database")
            return False
        return True
