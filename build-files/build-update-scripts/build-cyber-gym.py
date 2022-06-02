from google.cloud import storage
import secrets
import os.path
import subprocess

project_name = str(input(f"Input GCP project: "))
region = str("us-central1")
dns_suffix = str(input(f"Input DNS suffix for project (e.g. .example-cybergym.com): "))
admin_email = str(input(f"Provide an email address for the super administrator of this project: "))
api_key = str(input(f"Input the OAuth2.0 API Key for this project (from APIs and Services --> Credentials): "))

uniqueid = secrets.SystemRandom

# Move to the correct project
subprocess.call("gcloud config set project project_name", shell=True)

# Enable all of the necessary APIs
confirmation = str(input("Do you want to enable the necessary APIs at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud services enable compute.googleapis.com", shell=True)
    subprocess.call("gcloud services enable cloudfunctions.googleapis.com", shell=True)
    subprocess.call("gcloud services enable cloudbuild.googleapis.com", shell=True)
    subprocess.call("gcloud services enable pubsub.googleapis.com", shell=True)
    subprocess.call("gcloud services enable runtimeconfig.googleapis.com", shell=True)
    subprocess.call("gcloud services enable run.googleapis.com", shell=True)
    subprocess.call("gcloud services enable cloudscheduler.googleapis.com", shell=True)
    subprocess.call("gcloud services enable appengine.googleapis.com", shell=True)
    subprocess.call("gcloud services enable sqladmin.googleapis.com", shell=True)


# Create new user for Cloud Run functions
confirmation = str(input("Do you want to create the service account at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud iam service-accounts create cybergym-service --display-name 'Cyber Gym Service Account'", shell=True)
    subprocess.call("gcloud projects add-iam-policy-binding " + project_name + " --member=serviceAccount:cybergym-service@" + project_name + ".iam.gserviceaccount.com --role='roles/owner'", shell=True)
    subprocess.call("gcloud projects add-iam-policy-binding " + project_name + " --member=serviceAccount:cybergym-service@" + project_name + ".iam.gserviceaccount.com --role='roles/pubsub.admin'", shell=True)


# Create pubsub topics
confirmation = str(input("Do you want to create the pubsub topics for cloud functions at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud pubsub topics create build_arena", shell=True)
    subprocess.call("gcloud pubsub topics create build-workouts", shell=True)
    subprocess.call("gcloud pubsub topics create del-workout", shell=True)
    subprocess.call("gcloud pubsub topics create delete_arena", shell=True)
    subprocess.call("gcloud pubsub topics create maint-del-tmp-systems", shell=True)
    subprocess.call("gcloud pubsub topics create manage-server", shell=True)
    subprocess.call("gcloud pubsub topics create start-arena", shell=True)
    subprocess.call("gcloud pubsub topics create start-vm", shell=True)
    subprocess.call("gcloud pubsub topics create stop-all-servers", shell=True)
    subprocess.call("gcloud pubsub topics create stop-lapsed-arenas", shell=True)
    subprocess.call("gcloud pubsub topics create stop-workouts", shell=True)
    subprocess.call("gcloud pubsub topics create stop-vm", shell=True)
    subprocess.call("gcloud pubsub topics create db-update", shell=True)
    subprocess.call("gcloud pubsub topics create medic", shell=True)
    subprocess.call("gcloud pubsub topics create admin-scripts", shell=True)
    subprocess.call("gcloud pubsub topics create budget", shell=True)


# Create and copy over bucket files
confirmation = str(input("Do you want to copy over yaml files and instructions at this time? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    yamlpath = os.path.join(os.path.normpath(path) , r'\build-files\*.yaml')
    scriptpath = os.path.join(os.path.normpath(path) , r'\build-files\startup-scripts\*')
    introtocyberpath = os.path.join(os.path.normpath(path) , r'\build-files\intro-to-cyber\*.yaml')
    storage_client = storage.Client()
    assessment_upload_bucket = project_name + "_assessment_upload"
    bucket = storage_client.create_bucket(assessment_upload_bucket)
    cloudbuild_bucket = project_name + "_cloudbuild"
    bucket = storage_client.create_bucket(cloudbuild_bucket)
    student_instruction_bucket = 'student_workout_instructions_' + project_name
    bucket = storage_client.creat_bucket(student_instruction_bucket)
    teacher_instruction_bucket = 'teacher_workout_instructions_' + project_name
    bucket = storage_client.create_bucket(teacher_instruction_bucket)
    subprocess.call('gsutil cp scriptpath "gs://"' + project_name + '"_cloudbuild/startup-scripts/"', shell=True)
    subprocess.call('gsutil cp yamlpath "gs://"' + project_name + '"_cloudbuild/yaml-build-files/"', shell=True)
    subprocess.call('gsutil cp introtocyberpath "gs://"' + project_name + '"_cloudbuild/yaml-build-files/"', shell=True)
    subprocess.call('gsutil cp "gs://student_workout_instructions_tgd4419/*" "gs://student_workout_instructions_"' + project_name, shell=True)
    subprocess.call('gsutil cp "gs://teacher_workout_instructions_84jf627/*" "gs://teacher_workout_instructions_"' + project_name, shell=True)
    subprocess.call("gsutil acl ch -u AllUsers:R gs://student_workout_instructions_" + project_name, shell=True)
    subprocess.call("gsutil acl ch -u AllUsers:R gs://teacher_workout_instructions_" + project_name, shell=True)
    subprocess.call("gsutil acl ch -u AllUsers:R gs://" + project_name + "_assessment_upload", shell=True)
    subprocess.call("gsutil acl ch -r -u cybergym-service@" + project_name + ".iam.gserviceaccount.com:W gs://" + project_name + "_cloudbuild", shell=True)
    subprocess.call("gsutil acl ch -r -u AllUsers:R gs://" + project_name + "_cloudbuild/logo", shell=True)
    subprocess.call("gsutil acl ch -r -u AllUsers:R gs://" + project_name + "_cloudbuild/color", shell=True)


# Create project defaults
confirmation = str(input("Do you want to set project defaults at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud beta runtime-config configs create 'cybergym' --description 'Project constants for cloud functions and main app'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'project' " + project_name + " --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'region' 'us-central1' --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'zone" "us-central1-a' --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'dns_suffix' " + dns_suffix + " --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'script_repository' gs://" + project_name + "_cloudbuild/startup-scripts/ --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'api_key' " + api_key + " --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'main_app_url' 'https://cybergym" + dns_suffix + "' --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'admin_email' " + admin_email + " --config-name 'cybergym'", shell=True)
    sqlpassword = str(input("Type in the Shodan API? "))

# Create project database
confirmation = str(input("Do you want to create the mysql database at this time? (y/N): "))
if (confirmation == 'y'):
    sqlpassword = str(input("What would you like the SQL root password to be? You will not need to remember this "))

    subprocess.call("gcloud sql instances create cybergym --tier=db-g1-small --region=us-central", shell=True)
    subprocess.call("gcloud sql users set-password root --host=% --instance cybergym --password" + sqlpassword, shell=True)
    subprocess.call("gcloud sql databases create cybergym --instance=cybergym", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'sql_password' " + sqlpassword + " --config-name 'cybergym'", shell=True)
    ip_match = subprocess.call("gcloud sql instances describe cybergym | Select-String -Pattern '(ipAddress:\s)(\d+\.\d+\.\d+\.\d+)'", shell=True)
    subprocess.call("gcloud beta runtime-config configs variables set 'sql_ip' " + ip_match.Matches[0].Value + " --config-name 'cybergym'", shell=True)
    subprocess.call("gcloud sql instances patch cybergym --authorized-networks=0.0.0.0/0", shell=True)



# Create the cloud functions
confirmation = str(input("Before creating the cloud functions, you need to have a mirrored repo set up. Do you want to continue? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r'\cloud-functions')
    subprocess.call("gcloud functions deploy --quiet function-build-arena --region=" + region + " --memory=256MB --entry-point=cloud_fn_build_arena --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=build_arena", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-build-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_build_workout --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=build-workouts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-delete-expired-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_delete_expired_workout --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=maint-del-tmp-systems", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-manage-server --region=" + region + " --memory=256MB --entry-point=cloud_fn_manage_server --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=manage-server", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-start-arena --region=" + region + " --memory=256MB --entry-point=cloud_fn_start_arena --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=start-arena", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-start-vm --region=" + region + " --memory=256MB --entry-point=cloud_fn_start_vm --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=start-vm", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-lapsed-arenas --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_lapsed_arenas --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=stop-lapsed-arenas", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-lapsed-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_lapsed_workouts --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=stop-workouts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-vm --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_vm --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s  --trigger-topic=stop-vm", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-db-update --region=" + region + " --memory=256MB --entry-point=cloud_fn_db_update --runtime=python37 --source=$sourcepath --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=db-update", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-medic --region=" + region + " --memory=256MB --entry-point=cloud_fn_medic --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=medic", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-admin-scripts --region=" + region + " --memory=256MB --entry-point=cloud_fn_admin_scripts --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=admin-scripts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-budget-manager --region=" + region + " --memory=256MB --entry-point=cloud_fn_budget_manager --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=budget", shell=True)


# Create cloud schedules
confirmation = str(input("Do you want to create cloud schedules for cloud functions at this time? (y/N): "))
if (confirmation == 'y'):
    tz = str(input("What is your timezone? (America/Chicago) "))
    if (tz == ''):
        tz = "America/Chicago"

    subprocess.call('gcloud scheduler jobs create pubsub job-delete-expired-arenas --schedule="0 * * * *" --topic=maint-del-tmp-systems --time-zone=' + tz + ' --message-body=Hello! --attributes=workout_type=arena', shell=True)
    subprocess.call('gcloud scheduler jobs create pubsub job-stop-lapsed-arenas --schedule="*/15 * * * *" --topic=stop-lapsed-arenas --message-body=Hello!', shell=True)
    subprocess.call('gcloud scheduler jobs create pubsub maint-del-job --schedule="0 * * * *" --topic=maint-del-tmp-systems --message-body=Hello! --attributes=workout_type=workout', shell=True)
    subprocess.call('gcloud scheduler jobs create pubsub stop-workouts --schedule="*/15 * * * *" --topic=stop-workouts --message-body=Hello!', shell=True)
    subprocess.call('gcloud scheduler jobs create pubsub medic --schedule="*/10 * * * *" --topic=medic --message-body=Fix-Workouts', shell=True)
    subprocess.call('gcloud scheduler jobs create pubsub job-delete-misfits --schedule="0/15 * * * *" --topic=maint-del-tmp-systems --time-zone=' + tz + ' --message-body=Hello! --attributes=workout_type=misfit', shell=True)


# Copy over compute images for building workouts and arenas
confirmation = str(input("Do you want to copy over compute images at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud compute --project=" + project_name + " images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-account-control-v2 --source-image=image-cybergym-account-control-v2 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-activedirectory-domaincontroller --source-image= image-cybergym-activedirectory-domaincontroller --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-activedirectory-memberserver --source-image=image-cybergym-activedirectory-memberserver --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-arena-windows --source-image=image-cybergym-arena-windows --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-arena-windows-3 --source-image=image-cybergym-arena-windows-3 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-bufferoverflow --source-image=image-cybergym-bufferoverflow--source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-classified --source-image=image-cybergym-classified --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-cyberattack --source-image=image-cybergym-cyberattack --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-forensics-workstation --source-image=image-cybergym-forensics-workstation --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-fortinet-fortigate --source-image=image-cybergym-fortinet-fortigate --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-hiddensite --source-image=image-cybergym-hiddensite --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-nessus --source-image=image-cybergym-nessus --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-nessus-arena --source-image=image-cybergym-nessus-arena --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-password-policy-v2 --source-image=image-cybergym-password-policy-v2 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-ransomware --source-image=image-cybergym-ransomware --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-teenyweb --source-image=image-cybergym-teenyweb --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-tiny-hiddentarget --source-image=image-cybergym-tiny-hiddentarget --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-vnc --source-image=image-cybergym-vnc --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-wireshark --source-image=image-cybergym-wireshark --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-attacker --source-image=image-promise-attacker --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-victim-win2012 --source-image=image-promise-victim-win2012 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-vnc --source-image=image-promise-vnc --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-win-16 --source-image=image-promise-win-16 --source-image-project=ualr-cybersecurity", shell=True)


# Create main application
confirmation = str(input("Do you want to create the main application at this time? Please note, you must also set up a DNS CNAME pointing cybergym to ghs.googlehosted.com. (y/N): "))
if (confirmation == 'y'):
    path = r'..\..\\'
    sourcepath = os.path.join(os.path.normpath(path), r'main')
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io/" + project_name + "/cybergym", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io/" + project_name + "/cybergym --memory=512 --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com", shell=True)
    subprocess.call("gcloud beta run domain-mappings create --service cybergym --domain=cybergym" + dns_suffix + " --platform=managed --region=" + region, shell=True)


# Create the vulnerability defender application
confirmation = str(input("Do you want to create the vulnerability defender application? (y/N): "))
if (confirmation == 'y'):
    path = r'..\..\\'
    sourcepath = os.path.join(os.path.normpath(path), r'\container-applications\vulnerability-defender')
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io/" + project_name + "/vulnerability-defender", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io/" + project_name + "/vulnerability-defender --memory=256 --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service@" + project_name + ".iam.gserviceaccount.com", shell=True)
    subprocess.call("gcloud beta run domain-mappings create --service vulnerability-defender --domain=vulnerability-defender" + dns_suffix + " --platform=managed --region= " + region, shell=True)


# Create the iot configuration
confirmation = str(input("Do you want to create the IOT setup at this time? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud iot registries create cybergym-registry --region=" + region + " --event-notification-config=topic=cybergym-telemetry --state-pubsub-topic=cybergym-state", shell=True)

