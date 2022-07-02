from enum import Enum


class InstallUpdateTypes(Enum):
    FULL = 0
    UPDATE = 1
    CLOUD_FUNCTION = 2
    MAIN_APP = 3
    BUILD_SPECS = 4
    COMPUTE_IMAGES = 5
    INSTRUCTIONS = 6
    ENV = 7


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
        
    class ServiceAccount(str, Enum):
        CREATE_ACCOUNT = "gcloud iam service-accounts create cyberarena-service --display-name " \
                         "'Cyber Arena Service Account'"
        ADD_ROLE_OWNER = "gcloud projects add-iam-policy-binding {project} " \
                         "--member=serviceAccount:cyberarena-service@{project}.iam.gserviceaccount.com " \
                         "--role='roles/owner'"
        ADD_ROLE_PUBSUB = "gcloud projects add-iam-policy-binding {project} " \
                          "--member=serviceAccount:cyberarena-service@{project}.iam.gserviceaccount.com " \
                          "--role='roles/pubsub.admin'"

    class PubSubTopics(str, Enum):
        CYBER_ARENA = "gcloud pubsub topics create cyber_arena"
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
