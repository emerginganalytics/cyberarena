<#
BUILD CYBER GYM
---------------
This script uses gcloud and gsutil to build a new Cyber Gym for a Google Cloud Project

Preqrequisites:
    1. Create a mirrored bucket to the Cyber Gym repo at https://cloud.google.com/source-repositories/docs/mirroring-a-bitbucket-repository
    2. Enable the following APIs at https://console.cloud.google.com/apis/library
        a. Cloud Function APIs
        b. Cloud Build API
        c. App Engine Admin API
        d. Runtime Config API
        e. Compute API
        f. Cloud Run API
        g. Cloud Scheduler API


Post-Execution:
    1. Point DNS to the one indicated by the provided suffix
    2. Increase quotas according the following recommendations based on Max Concurrent Build (MCB)
        a. Compute Engine API (Subnetworks) - MCB * 2
        b. Compute Engine API (Networks) - MCB * 1
        c. Compute Engine API (Firewall Rules) - MCB * 3
        d. Compute Engine API (Routes) - MCB * 2
        e. Compute Engine API (In-Use IP Addresses) - MCB * 1
        f. Compute Engine API (CPUs) - MCB * 3
        g. Cloud Build API (Concurrent Builds) - 50
#>

 param (
    [string]$project = $( Read-Host "Input GCP project:" ),
    [string]$region = "us-central1",
    [string]$dns_suffix = $( Read-Host "Input DNS suffix for project (e.g. .example-cybergym.com)" )

 )
$uniqueid = Get-Random

# Move to the correct project
gcloud config set project $project

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
}

# Create and copy over bucket files
$confirmation = Read-Host "Do you want to copy over yaml files and instructions at this time? (y/N)"
if ($confirmation -eq 'y') {
    gsutil mb gs://"$project"_cloudbuild
    gsutil mb gs://student_workout_instructions_"$project"
    gsutil mb gs://teacher_workout_instructions_"$project"
    gsutil cp gs://ualr-cybersecurity_cloudbuild/startup-scripts/* gs://"$project"_cloudbuild/startup-scripts/
    gsutil cp gs://ualr-cybersecurity_cloudbuild/yaml-build-files/* gs://"$project"_cloudbuild/yaml-build-files/
    gsutil cp gs://student_workout_instructions_tgd4419/* gs://student_workout_instructions_"$project"
    gsutil cp gs://teacher_workout_instructions_84jf627/* gs://teacher_workout_instructions_"$project"
    gsutil acl ch -u AllUsers:R gs://student_workout_instructions_"$project"
    gsutil acl ch -u AllUsers:R gs://teacher_workout_instructions_"$project"
    gsutil acl ch -r -u cybergym-service@"$project".iam.gserviceaccount.com:R gs://"$project"_cloudbuild
}

# Create project defaults
$confirmation = Read-Host "Do you want to set project defaults at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud beta runtime-config configs create "cybergym" --description "Project constants for cloud functions and main app"
    gcloud beta runtime-config configs variables set "project" $project --config-name "cybergym"
    gcloud beta runtime-config configs variables set "region" "us-central1" --config-name "cybergym"
    gcloud beta runtime-config configs variables set "zone" "us-central1-a" --config-name "cybergym"
    gcloud beta runtime-config configs variables set "dns_suffix" $dns_suffix --config-name "cybergym"
}

# Create the cloud functions
$confirmation = Read-Host "Before creating the cloud functions, you need to have a mirrored repo set up. Do you want to continue? (y/N)"
if ($confirmation -eq 'y') {
    # proceed
    gcloud functions deploy --quiet function-build-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_arena `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=build_arena
    gcloud functions deploy --quiet function-build-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_workout `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=build-workouts
    gcloud functions deploy --quiet function-delete-expired-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_workout `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=maint-del-tmp-systems
    gcloud functions deploy --quiet function-delete-expired-arenas `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_arenas `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=delete_arena
    gcloud functions deploy --quiet function-manage-server `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_manage_server `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=manage-server
    gcloud functions deploy --quiet function-start-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_arena `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=start-arena
    gcloud functions deploy --quiet function-start-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_vm `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=start-vm
    gcloud functions deploy --quiet function-stop-all-servers `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_all_servers `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=stop-all-servers
    gcloud functions deploy --quiet function-stop-lapsed-arenas `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_arenas `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=stop-lapsed-arenas
    gcloud functions deploy --quiet function-stop-lapsed-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_workouts `
        --runtime=python37 `
        --source=https://source.developers.google.com/projects/$project/repos/bitbucket_eac-ualr_cybergym/moveable-aliases/master/paths/cloud-functions `
        --timeout=540s `
        --trigger-topic=stop-workouts
}


# Create DNS Zone
$confirmation = Read-Host "Do you want to set up the DNS Zone at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud dns managed-zones create cybergym-public --dns-name "$dns_suffix" --description "A zone for dynamically updating the DNS for Cyber Gym builds"
}

# Create cloud schedules
$confirmation = Read-Host "Do you want to create cloud schedules for cloud functions at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud scheduler jobs create pubsub job-delete-expired-arenas --schedule="0 * * * *" --topic=delete_arena --message-body=Hello!
    gcloud scheduler jobs create pubsub job-stop-all-servers --schedule="0 0 * * *" --topic=stop-all-servers --message-body=Hello!
    gcloud scheduler jobs create pubsub job-stop-lapsed-arenas --schedule="*/15 * * * *" --topic=stop-lapsed-arenas --message-body=Hello!
    gcloud scheduler jobs create pubsub maint-del-job --schedule="0 * * * *" --topic=maint-del-tmp-systems --message-body=Hello!
    gcloud scheduler jobs create pubsub stop-workouts --schedule="*/15 * * * *" --topic=stop-workouts --message-body=Hello!
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
$sourcepath = Join-Path (Resolve-Path .\).Path "ualr_maintainer"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cybergym
    gcloud run deploy --image gcr.io/$project/cybergym --memory=512 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
    gcloud beta run domain-mappings create --service cybergym --domain=cybergym"$dns_suffix" --platform=managed --region=$region
}
