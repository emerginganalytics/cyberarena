from enum import Enum
from collections import namedtuple

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class SetupOptions(bytes, Enum):
    def __new__(cls, value, description):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.description = description
        return obj

    FULL = (0, "Full Cyber Arena Installation")
    UPDATE = (1, "Update Main Application and Cloud Functions")
    CLOUD_FUNCTION = (2, "Update Cloud Function Only")
    MAIN_APP = (3, "Update Main Application Only")
    BUILD_SPECS = (4, "Synchronize Build Specifications, Instructions, and Compute Images")
    ENV = (5, "Synchronize Environment Variables")
    EXIT = (6, "Exit")


class ShellCommands:   
    class EnableAPIs(str, Enum):
        COMPUTE = "gcloud services enable compute.googleapis.com"
        FUNCTIONS = "gcloud services enable cloudfunctions.googleapis.com"
        CLOUD_BUILD = "gcloud services enable cloudbuild.googleapis.com"
        PUB_SUB = "gcloud services enable pubsub.googleapis.com"
        RUNTIME_CONFIG = "gcloud services enable runtimeconfig.googleapis.com"
        CLOUD_RUN = "gcloud services enable run.googleapis.com"
        SCHEDULER = "gcloud services enable cloudscheduler.googleapis.com"
        APP_ENGINE = "gcloud services enable appengine.googleapis.com"
        SQL_ADMIN = "gcloud services enable sqladmin.googleapis.com"
        IAM = "gcloud services enable iam.googleapis.com"
        
    class ServiceAccount(str, Enum):
        CREATE_ACCOUNT = "gcloud iam service-accounts create cyberarena-service --display-name " \
                         "\"Cyber Arena Service Account\""
        ADD_ROLE_OWNER = "gcloud projects add-iam-policy-binding {project} " \
                         "--member=serviceAccount:cyberarena-service@{project}.iam.gserviceaccount.com " \
                         "--role=\"roles/owner\""
        ADD_ROLE_PUBSUB = "gcloud projects add-iam-policy-binding {project} " \
                          "--member=serviceAccount:cyberarena-service@{project}.iam.gserviceaccount.com " \
                          "--role=\"roles/pubsub.admin\""
        ADD_ROLE_STORAGE = "gcloud projects add-iam-policy-binding {project} " \
                           "--member=serviceAccount:cyberarena-service@{project}.iam.gserviceaccount.com " \
                           "--role=\"roles/storage.admin\""

    class PubSubTopics(str, Enum):
        CYBER_ARENA = "gcloud pubsub topics create cyber-arena"
        BUDGET = "gcloud pubsub topics create budget"

    class EnvironmentVariables(str, Enum):
        PROJECT = "gcloud beta runtime-config configs variables set 'project' {project} --config-name 'cybergym'"
        REGION = "gcloud beta runtime-config configs variables set 'region' {region} --config-name 'cybergym'"
        ZONE = "gcloud beta runtime-config configs variables set 'zone' {zone} --config-name 'cybergym'"
        DNS_SUFFIX = "gcloud beta runtime-config configs variables set 'dns_suffix' {dns_suffix} " \
                     "--config-name 'cybergym'"
        SCRIPT_REPOSITORY = "gcloud beta runtime-config configs variables set 'script_repository' " \
                            "gs://{project}_cloudbuild/startup-scripts/ --config-name 'cybergym'"
        FIREBASE_API_KEY = "gcloud beta runtime-config configs variables set 'api_key' {firebase_api_key} " \
                           "--config-name 'cybergym'"
        MAIN_APP_URL = "gcloud beta runtime-config configs variables set 'main_app_url' '{main_app_url}' " \
                       "--config-name 'cybergym'"
        ADMIN_EMAIL = "gcloud beta runtime-config configs variables set 'admin_email' {admin_email} " \
                      "--config-name 'cybergym'"
