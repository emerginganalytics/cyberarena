<#
CREATE CHILD GYM
---------------
Creates a child cyber gym and links it to a parent project. The distinction between the two is described as follows:

Parent: Runs all of the applictions, maintains the datastore entity, and manages the DNS
Child: Runs the cloud functions necessary for building a Cyber Arena

Don't forget to increase quotas according the following recommendations based on Max Concurrent Build (MCB)
        a. Compute Engine API (Subnetworks) - MCB * 2
        b. Compute Engine API (Networks) - MCB * 1
        c. Compute Engine API (Firewall Rules) - MCB * 3
        d. Compute Engine API (Routes) - MCB * 2
        e. Compute Engine API (CPUs) - MCB * 3
        f.
 #>
#>
 param (
    [string]$child_project = $( Read-Host "Input Child project name:" ),
    [string]$parent_project = $( Read-Host "Input Parent project name:" ),
    [string]$region = "us-central1"
 )

# Move to the correct project
gcloud config set project $child_project

# Determine if this is a creation or update
$run_type = Read-Host "Do you want to create a new child project or update an existing one? ([n]ew/[U]pdate)"
if ($run_type.ToLower().StartsWith("n")) {
    $dns_suffix = Read-Host "Input DNS suffix from the PARENT project (e.g. .example-cybergym.com)"
    $admin_email = Read-Host "Provide an email address for the super administrator of this project:"

    # Enable all of the necessary APIs
    $confirmation = Read-Host "Do you want to enable the necessary APIs for the child at this time? (y/N)"
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

    # Provide the permissions for the parent service account to manage the child project.
    $confirmation = Read-Host "Do you want to create the child service account and add privileges for the parent service account at this time? (y/N)"
    if ($confirmation -eq 'y') {
        gcloud iam service-accounts create cybergym-service --display-name "Cyber Gym Service Account"
        gcloud projects add-iam-policy-binding $parent_project --member=serviceAccount:cybergym-service@"$child_project".iam.gserviceaccount.com --role='roles/owner'
        gcloud projects add-iam-policy-binding $parent_project --member=serviceAccount:cybergym-service@"$child_project".iam.gserviceaccount.com --role='roles/datastore.owner'
        gcloud projects add-iam-policy-binding $child_project --member=serviceAccount:cybergym-service@"$child_project".iam.gserviceaccount.com --role='roles/owner'
        gcloud projects add-iam-policy-binding $child_project --member=serviceAccount:cybergym-service@"$child_project".iam.gserviceaccount.com --role='roles/pubsub.admin'
        gcloud projects add-iam-policy-binding $child_project --member=serviceAccount:cybergym-service@"$parent_project".iam.gserviceaccount.com --role='roles/owner'
        gcloud projects add-iam-policy-binding $child_project --member=serviceAccount:cybergym-service@"$parent_project".iam.gserviceaccount.com --role='roles/pubsub.admin'
        gcloud iam service-accounts add-iam-policy-binding cybergym-service@"$parent_project".iam.gserviceaccount.com --member=$MEMBER --role='roles/iam.serviceAccountUser'
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
    }

    # Create project defaults
    $confirmation = Read-Host "Do you want to set project defaults at this time? (y/N)"
    if ($confirmation -eq 'y') {
        gcloud beta runtime-config configs create "cybergym" --description "Project constants for cloud functions and main app"
        gcloud beta runtime-config configs variables set "project" $child_project --config-name "cybergym"
        gcloud beta runtime-config configs variables set "parent_project" $parent_project --config-name "cybergym"
        gcloud beta runtime-config configs variables set "region" "us-central1" --config-name "cybergym"
        gcloud beta runtime-config configs variables set "zone" "us-central1-a" --config-name "cybergym"
        gcloud beta runtime-config configs variables set "script_repository" gs://"$parent_project"_cloudbuild/startup-scripts/ --config-name "cybergym"
        gcloud beta runtime-config configs variables set "dns_suffix" $dns_suffix --config-name "cybergym"
        gcloud beta runtime-config configs variables set "script_repository" gs://"$project"_cloudbuild/startup-scripts/ --config-name "cybergym"
        gcloud beta runtime-config configs variables set "main_app_url" "https://cybergym$dns_suffix" --config-name "cybergym"
        gcloud beta runtime-config configs variables set "admin_email" $admin_email --config-name "cybergym"
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
    $confirmation = Read-Host "Do you want to copy over machine-images at this time? (y/N)"
    if ($confirmation -eq 'y')
    {

        gcloud beta compute machine-images add-iam-policy-binding image-fortimanager --project $child_project --member serviceAccount: cybergym-service@$child_project.iam.gserviceaccount.com --role roles/compute.admin
        gcloud compute networks create cybergymfortinet-external-network --subnet-mode custom
        gcloud compute networks subnets create cybergymfortinet-external-network-default --network cybergymfortinet-external-network --range 10.1.0.0/24
        gcloud compute networks create cybergymfortinet-dmz-network --subnet-mode custom
        gcloud compute networks subnets create cybergymfortinet-dmz-network-default --network cybergymfortinet-dmz-network --range 10.1.2.0/24
        gcloud compute networks create cybergymfortinet-internal-network --subnet-mode custom
        gcloud compute networks subnets create cybergymfortinet-internal-network-default --network cybergymfortinet-internal-network --range 10.1.1.0/24
        gcloud beta compute instances create cybergym-fortimanager --project $child_project --zone us-central1-a --source-machine-image projects/ualr-cybersecurity/global/machineImages/image-fortimanager --service-account cybergym-service@$child_project.iam.gserviceaccount.com
        gcloud beta compute machine-images create image-fortimanager --source-instance cybergym-fortimanager  --source-instance-zone us-central1-a
    }
}
# Create the cloud functions
$confirmation = Read-Host "Do you want to create or update the cloud functions at this time? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\).Path "\cloud-functions"
    gcloud functions deploy --quiet function-build-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=build_arena
    gcloud functions deploy --quiet function-build-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=build-workouts
    gcloud functions deploy --quiet function-delete-expired-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=maint-del-tmp-systems
    gcloud functions deploy --quiet function-manage-server `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_manage_server `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=manage-server
    gcloud functions deploy --quiet function-start-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=start-arena
    gcloud functions deploy --quiet function-start-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=start-vm
    gcloud functions deploy --quiet function-stop-lapsed-arenas `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_arenas `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-lapsed-arenas
    gcloud functions deploy --quiet function-stop-lapsed-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_workouts `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-workouts
    gcloud functions deploy --quiet function-stop-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=stop-vm
    gcloud functions deploy --quiet function-medic `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_medic `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=medic
    gcloud functions deploy --quiet function-admin-scripts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_admin_scripts `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$child_project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=admin-scripts
}

# Copy over compute images for building workouts and arenas
$confirmation = Read-Host "Do you want to copy over ALL compute images at this time? (y/N)"
if ($confirmation -eq 'y') {
    gcloud compute --project=$child_project images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-arena-windows --source-image=image-cybergym-arena-windows --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-arena-windows-3 --source-image=image-cybergym-arena-windows-3 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-bufferoverflow --source-image=image-cybergym-bufferoverflow --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-classified --source-image=image-cybergym-classified --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-cyberattack --source-image=image-cybergym-cyberattack --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-forensics-workstation --source-image=image-cybergym-forensics-workstation --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-fortinet-fortigate --source-image=image-cybergym-fortinet-fortigate --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-hiddensite --source-image=image-cybergym-hiddensite --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-nessus --source-image=image-cybergym-nessus --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-nessus-arena --source-image=image-cybergym-nessus-arena --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-password-policy-v2 --source-image=image-cybergym-password-policy-v2 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-ransomware --source-image=image-cybergym-ransomware --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-teenyweb --source-image=image-cybergym-teenyweb --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-tiny-hiddentarget --source-image=image-cybergym-tiny-hiddentarget --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-vnc --source-image=image-cybergym-vnc --source-image-project=ualr-cybersecurity
    gcloud compute --project=$child_project images create image-cybergym-wireshark --source-image=image-cybergym-wireshark --source-image-project=ualr-cybersecurity
}

$confirmation = Read-Host "Do you want to copy over INDIVIDUAL cloud images? (y/N)"
if ($confirmation -eq 'y') {
    $images = Read-Host "  Provide a comma-separated list of images to copy over"
    foreach ($image in $images.Split(","))
    {
        gcloud compute --project $child_project images delete $image --quiet
        gcloud compute --project $child_project images create $image --source-image $image --source-image-project ualr-cybersecurity
    }
}