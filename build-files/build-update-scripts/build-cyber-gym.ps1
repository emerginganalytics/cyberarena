<#
BUILD CYBER GYM
---------------
This script uses gcloud and gsutil to build a new Cyber Gym for a Google Cloud Project

Preqrequisites:
    1. Set up the Identity Platform service and obtain the API key as specified in the documentation.
    2. Enable the DNS service and create a new managed domain
    3. Increase quotas according the following recommendations based on Max Concurrent Build (MCB)
        a. Compute Engine API (Subnetworks) - MCB * 2
        b. Compute Engine API (Networks) - MCB * 1
        c. Compute Engine API (Firewall Rules) - MCB * 3
        d. Compute Engine API (Routes) - MCB * 2
        e. Compute Engine API (In-Use IP Addresses) - MCB * 1
        f. Compute Engine API (CPUs) - MCB * 3
        g. Cloud Build API (Concurrent Builds) - 50

Post Setup:
    Create a budget value with a PubSub sending to the 'budget' topic. Also include budget nofications
    for exceeding budgets (e.g., 110%, 120%, etc.) See
    https://cloud.google.com/billing/docs/how-to/notify#set_up_budget_notifications
#>

 param (
    [string]$project = $( Read-Host "Input GCP project:" ),
    [string]$region = "us-central1",
    [string]$dns_suffix = $( Read-Host "Input DNS suffix for project (e.g. .example-cybergym.com)" ),
    [string]$admin_email = $( Read-Host "Provide an email address for the super administrator of this project:"),
    [string]$api_key = $( Read-Host "Input the OAuth2.0 API Key for this project (from APIs and Services --> Credentials)" )
 )
$uniqueid = Get-Random

# Move to the correct project
gcloud config set project $project

# Enable all of the necessary APIs
$confirmation = Read-Host "Do you want to enable the necessary APIs at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud services enable compute.googleapis.com 
    gcloud services enable cloudfunctions.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable pubsub.googleapis.com
    gcloud services enable runtimeconfig.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable cloudscheduler.googleapis.com
    gcloud services enable appengine.googleapis.com
    gcloud services enable sqladmin.googleapis.com
}

# Create new user for Cloud Run functions
$confirmation = Read-Host "Do you want to create the service account at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud iam service-accounts create cybergym-service --display-name "Cyber Gym Service Account"
    gcloud projects add-iam-policy-binding $project --member=serviceAccount:cybergym-service@"$project".iam.gserviceaccount.com --role='roles/owner'
    gcloud projects add-iam-policy-binding $project --member=serviceAccount:cybergym-service@"$project".iam.gserviceaccount.com --role='roles/pubsub.admin'
}

# Create pubsub topics
$confirmation = Read-Host "Do you want to create the pubsub topics for cloud functions at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud pubsub topics create build_arena
    gcloud pubsub topics create build-workouts
    gcloud pubsub topics create del-workout
    gcloud pubsub topics create delete_arena
    gcloud pubsub topics create maint-del-tmp-systems
    gcloud pubsub topics create manage-server
    gcloud pubsub topics create start-arena
    gcloud pubsub topics create start-vm
    gcloud pubsub topics create stop-all-servers
    gcloud pubsub topics create stop-lapsed-arenas
    gcloud pubsub topics create stop-workouts
    gcloud pubsub topics create stop-vm
    gcloud pubsub topics create db-update
    gcloud pubsub topics create medic
    gcloud pubsub topics create admin-scripts
    gcloud pubsub topics create budget
}

# Create and copy over bucket files
$confirmation = Read-Host "Do you want to copy over yaml files and instructions at this time? (y/N)"
if ($confirmation -eq 'y') {
    $yamlpath = Join-Path (Resolve-Path ..\).Path "\build-files\*.yaml"
    $scriptpath = Join-Path (Resolve-Path ..\).Path "\build-files\startup-scripts\*"
    $introtocyberpath = Join-Path (Resolve-Path ..\).Path "\build-files\intro-to-cyber\*.yaml"
    gsutil mb gs://"$project"_assessment_upload
    gsutil mb gs://"$project"_cloudbuild
    gsutil mb gs://student_workout_instructions_"$project"
    gsutil mb gs://teacher_workout_instructions_"$project"
    gsutil cp $scriptpath gs://"$project"_cloudbuild/startup-scripts/
    gsutil cp $yamlpath gs://"$project"_cloudbuild/yaml-build-files/
    gsutil cp $introtocyberpath gs://"$project"_cloudbuild/yaml-build-files/
    gsutil cp gs://student_workout_instructions_tgd4419/* gs://student_workout_instructions_"$project"
    gsutil cp gs://teacher_workout_instructions_84jf627/* gs://teacher_workout_instructions_"$project"
    gsutil acl ch -u AllUsers:R gs://student_workout_instructions_"$project"
    gsutil acl ch -u AllUsers:R gs://teacher_workout_instructions_"$project"
    gsutil acl ch -u AllUsers:R gs://"$project"_assessment_upload
    gsutil acl ch -r -u cybergym-service@"$project".iam.gserviceaccount.com:W gs://"$project"_cloudbuild
    gsutil acl ch -r -u AllUsers:R gs://"$project"_cloudbuild/logo
    gsutil acl ch -r -u AllUsers:R gs://"$project"_cloudbuild/color
}

# Create project defaults
$confirmation = Read-Host "Do you want to set project defaults at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud beta runtime-config configs create "cybergym" --description "Project constants for cloud functions and main app"
    gcloud beta runtime-config configs variables set "project" $project --config-name "cybergym"
    gcloud beta runtime-config configs variables set "region" "us-central1" --config-name "cybergym"
    gcloud beta runtime-config configs variables set "zone" "us-central1-a" --config-name "cybergym"
    gcloud beta runtime-config configs variables set "dns_suffix" $dns_suffix --config-name "cybergym"
    gcloud beta runtime-config configs variables set "script_repository" gs://"$project"_cloudbuild/startup-scripts/ --config-name "cybergym"
    gcloud beta runtime-config configs variables set "api_key" $api_key --config-name "cybergym"
    gcloud beta runtime-config configs variables set "main_app_url" "https://cybergym$dns_suffix" --config-name "cybergym"
    gcloud beta runtime-config configs variables set "admin_email" $admin_email --config-name "cybergym"
    $sqlpassword = Read-Host "Type in the Shodan API? "
}
# Create project database
$confirmation = Read-Host "Do you want to create the mysql database at this time? (y/N)"
if ($confirmation -eq 'y') {
    $sqlpassword = Read-Host "What would you like the SQL root password to be? You will not need to remember this "

    gcloud sql instances create cybergym --tier=db-g1-small --region=us-central
    gcloud sql users set-password root --host=% --instance cybergym --password $sqlpassword
    gcloud sql databases create cybergym --instance=cybergym
    gcloud beta runtime-config configs variables set "sql_password" $sqlpassword --config-name "cybergym"
    $ip_match = gcloud sql instances describe cybergym | Select-String -Pattern "(ipAddress:\s)(\d+\.\d+\.\d+\.\d+)"
    gcloud beta runtime-config configs variables set "sql_ip" $ip_match.Matches[0].Value --config-name "cybergym"
    gcloud sql instances patch cybergym --authorized-networks=0.0.0.0/0
}


# Create the cloud functions
$confirmation = Read-Host "Before creating the cloud functions, you need to have a mirrored repo set up. Do you want to continue? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\cloud-functions"
    gcloud functions deploy --quiet function-build-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=build_arena
    gcloud functions deploy --quiet function-build-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=build-workouts
    gcloud functions deploy --quiet function-delete-expired-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=maint-del-tmp-systems
    gcloud functions deploy --quiet function-manage-server `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_manage_server `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=manage-server
    gcloud functions deploy --quiet function-start-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=start-arena
    gcloud functions deploy --quiet function-start-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=start-vm
    gcloud functions deploy --quiet function-stop-lapsed-arenas `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_arenas `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-lapsed-arenas
    gcloud functions deploy --quiet function-stop-lapsed-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_workouts `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-workouts
    gcloud functions deploy --quiet function-stop-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-vm
    gcloud functions deploy --quiet function-db-update `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_db_update `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=db-update
    gcloud functions deploy --quiet function-medic `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_medic `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=medic
    gcloud functions deploy --quiet function-admin-scripts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_admin_scripts `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=admin-scripts
    gcloud functions deploy --quiet function-budget-manager `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_budget_manager `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=budget
}

# Create cloud schedules
$confirmation = Read-Host "Do you want to create cloud schedules for cloud functions at this time? (y/N)"
if ($confirmation -eq 'y') {
    $tz = Read-Host "What is your timezone? (America/Chicago) "
    if ($tz -eq '') {
        $tz = "America/Chicago"
    }
    gcloud scheduler jobs create pubsub job-delete-expired-arenas --schedule="0 * * * *" --topic=maint-del-tmp-systems --time-zone=$tz --message-body=Hello! --attributes=workout_type=arena
    gcloud scheduler jobs create pubsub job-stop-lapsed-arenas --schedule="*/15 * * * *" --topic=stop-lapsed-arenas --message-body=Hello!
    gcloud scheduler jobs create pubsub maint-del-job --schedule="0 * * * *" --topic=maint-del-tmp-systems --message-body=Hello! --attributes=workout_type=workout
    gcloud scheduler jobs create pubsub stop-workouts --schedule="*/15 * * * *" --topic=stop-workouts --message-body=Hello!
    gcloud scheduler jobs create pubsub medic --schedule="*/10 * * * *" --topic=medic --message-body=Fix-Workouts
    gcloud scheduler jobs create pubsub job-delete-misfits --schedule="0/15 * * * *" --topic=maint-del-tmp-systems --time-zone=$tz --message-body=Hello! --attributes=workout_type=misfit
}

# Copy over compute images for building workouts and arenas
$confirmation = Read-Host "Do you want to copy over compute images at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud compute --project=$project images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-account-control-v2 --source-image=image-cybergym-account-control-v2 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-activedirectory-domaincontroller --source-image= image-cybergym-activedirectory-domaincontroller --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-activedirectory-memberserver --source-image=image-cybergym-activedirectory-memberserver --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-arena-windows --source-image=image-cybergym-arena-windows --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-arena-windows-3 --source-image=image-cybergym-arena-windows-3 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-bufferoverflow --source-image=image-cybergym-bufferoverflow--source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-classified --source-image=image-cybergym-classified --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-cyberattack --source-image=image-cybergym-cyberattack --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-forensics-workstation --source-image=image-cybergym-forensics-workstation --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-fortinet-fortigate --source-image=image-cybergym-fortinet-fortigate --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-hiddensite --source-image=image-cybergym-hiddensite --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-nessus --source-image=image-cybergym-nessus --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-nessus-arena --source-image=image-cybergym-nessus-arena --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-password-policy-v2 --source-image=image-cybergym-password-policy-v2 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-ransomware --source-image=image-cybergym-ransomware --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-teenyweb --source-image=image-cybergym-teenyweb --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-tiny-hiddentarget --source-image=image-cybergym-tiny-hiddentarget --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-vnc --source-image=image-cybergym-vnc --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-wireshark --source-image=image-cybergym-wireshark --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-promise-attacker --source-image=image-promise-attacker --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-promise-victim-win2012 --source-image=image-promise-victim-win2012 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-promise-vnc --source-image=image-promise-vnc --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-promise-win-16 --source-image=image-promise-win-16 --source-image-project=ualr-cybersecurity
}

# Create main application
$confirmation = Read-Host "Do you want to create the main application at this time? Please note, you must also set up a DNS CNAME pointing cybergym to ghs.googlehosted.com. (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "main"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cybergym
    gcloud run deploy --image gcr.io/$project/cybergym --memory=512 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
    gcloud beta run domain-mappings create --service cybergym --domain=cybergym"$dns_suffix" --platform=managed --region=$region
}

# Create the vulnerability defender application
$confirmation = Read-Host "Do you want to create the vulnerability defender application? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\vulnerability-defender"
    gcloud builds submit $sourcepath --tag gcr.io/$project/vulnerability-defender
    gcloud run deploy --image gcr.io/$project/vulnerability-defender --memory=256 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
    gcloud beta run domain-mappings create --service vulnerability-defender --domain=vulnerability-defender"$dns_suffix" --platform=managed --region=$region
}

# Create the iot configuration
$confirmation = Read-Host "Do you want to create the IOT setup at this time? (y/N)"
if ($confirmation -eq 'y')
{
    gcloud iot registries create cybergym-registry --region=$region --event-notification-config=topic=cybergym-telemetry --state-pubsub-topic=cybergym-state
}
