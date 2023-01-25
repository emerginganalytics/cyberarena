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
    BUILD_SPECS = (4, "Synchronize and Encrypt/Decrypt Build Specifications, Instructions, and Compute Images.")
    PREPARE_SPEC = (5, "Prepare a single specification for deployment")
    DECRYPT_SPECS = (6, "Decrypt Build Specifications")
    ENV = (7, "Synchronize Environment Variables")
    BULK_UPDATE = (8, "Update multiple cloud projects at once")
    EXIT = (9, "Exit")


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

    class RuntimeConfig(str, Enum):
        CREATE_RUNTIME_CONFIG = "gcloud beta runtime-config configs create \"cybergym\" " \
                                "--description \"Project constants for cloud functions and main app\""


class InstallSettings:
    BULK_SETTINGS_FILENAME = ".bulk_settings.yaml"
