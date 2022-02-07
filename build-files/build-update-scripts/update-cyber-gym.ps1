 param (
    [string]$project = $( Read-Host "Input GCP project:" ),
    [string]$region = "us-central1"
 )
 
# Move to the correct project
gcloud config set project $project

# Update the main application
$confirmation = Read-Host "Do you want to update the main applications? (y/N)"
if ($confirmation -eq 'y') {
    $app = Read-Host "What is the application name? (cybergym) "
    if ($app -eq 'y') {
        $app = "cybergym"
    }
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\main"
    gcloud builds submit $sourcepath --tag gcr.io/$project/$app
    gcloud run deploy "$app" --image gcr.io/"$project"/"$app" --memory=1024Mi --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

# Update cybergym-classified
$confirmation = Read-Host "Do you want to update cybergym-classified? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\classified"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cybergym-classified
    gcloud run deploy --image gcr.io/$project/cybergym-classified --memory=256 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

# Update Shodan
$confirmation = Read-Host "Do you want to update cybergym-shodanlite? (y/N)"
if ($confirmation -eq 'y') {
    [string]$shodan_api_key = $( Read-Host "Input the Shodan API Key:" )
    gcloud beta runtime-config configs variables set "SHODAN_API_KEY" $shodan_api_key --config-name "cybergym"
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\Shodan"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cybergym-shodanlite
    gcloud run deploy --image gcr.io/$project/cybergym-shodanlite --memory=256 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

# Update Arena Snake
$confirmation = Read-Host "Do you want to update Arena Snake? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\Arena Snake"
    gcloud builds submit $sourcepath --tag gcr.io/$project/arena-snake-loader
    gcloud run deploy --image gcr.io/$project/arena-snake-loader --memory=256 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

# Update JohnnyHash
$confirmation = Read-Host "Do you want to update Johnny Hash Crypto Server? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\JohnnyHash"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cryptoserver
    gcloud run deploy --image gcr.io/$project/cryptoserver --memory=256Mi --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

$confirmation = Read-Host "Do you want to update IoT webserver? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\IoT"
    gcloud builds submit $sourcepath --tag gcr.io/$project/nsa-healthcare
    gcloud run deploy --image gcr.io/$project/nsa-healthcare --memory=256Mi --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

 # Update vulnerability_defender
$confirmation = Read-Host "Do you want to update Vulnerability Defender? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\vulnerability-defender"
    gcloud builds submit $sourcepath --tag gcr.io/$project/vulnerability-defender
    gcloud run deploy --image gcr.io/$project/vulnerability-defender --memory=256 --platform=managed --region=$region --allow-unauthenticated --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

 # Update the Capability Maturity Model Assessment
$confirmation = Read-Host "Do you want to update the CMMC assessment? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\container-applications\Assessment-Form"
    gcloud builds submit $sourcepath --tag gcr.io/$project/cmmc-assessment
    gcloud run deploy --image gcr.io/$project/cmmc-assessment --memory=512 --platform=managed --region=$region --service-account=cybergym-service@"$project".iam.gserviceaccount.com
}

# Create the cloud functions
$confirmation = Read-Host "Do you want to update ALL cloud functions? (y/N)"
if ($confirmation -eq 'y') {
    $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\cloud-functions"
    gcloud functions deploy --quiet function-build-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=build_arena
    gcloud functions deploy --quiet function-build-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_build_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=build-workouts
    gcloud functions deploy --quiet function-delete-expired-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=maint-del-tmp-systems
    gcloud functions deploy --quiet function-manage-server `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_manage_server `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=manage-server
    gcloud functions deploy --quiet function-start-arena `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_arena `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=start-arena
    gcloud functions deploy --quiet function-start-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_start_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=start-vm
    gcloud functions deploy --quiet function-stop-lapsed-arenas `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_arenas `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=stop-lapsed-arenas
    gcloud functions deploy --quiet function-stop-lapsed-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_lapsed_workouts `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=stop-workouts
    gcloud functions deploy --quiet function-stop-vm `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_stop_vm `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=stop-vm
    gcloud functions deploy --quiet function-medic `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_medic `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=medic
    gcloud functions deploy --quiet function-iot-capture-sensor `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_iot_capture_sensor `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=cybergym-telemetry
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

$confirmation = Read-Host "Do you want to update INDIVIDUAL cloud functions? (y/N)"
if ($confirmation -eq 'y') {
    DO
    {
        $function = Read-Host "  Which function would you like to update?"
        $entry = Read-Host "  What is the entry-point function?"
        $topic = Read-Host "  What is the pub-sub-topic?"
        $sourcepath = Join-Path (Resolve-Path ..\..\).Path "\cloud-functions"
        gcloud functions deploy --quiet $function `
            --region=$region `
            --memory=256MB `
            --entry-point=$entry `
            --runtime=python37 `
            --source=$sourcepath `
            --timeout=540s `
            --trigger-topic=$topic
        $confirmation = Read-Host "Do you want to update any more cloud functions? (y/N)"

    } While ($confirmation –eq ‘y’)
}

$confirmation = Read-Host "Do you want to update build yaml specifications and startup scripts? (y/N)"
if ($confirmation -eq 'y') {
    $yamlpath = Join-Path (Resolve-Path ..\).Path "\build-files\*.yaml"
    $introtocyberpath = Join-Path (Resolve-Path ..\).Path "\build-files\intro-to-cyber\*.yaml"
    $scriptpath = Join-Path (Resolve-Path ..\).Path "\build-files\startup-scripts\*"
    gsutil cp $scriptpath gs://"$project"_cloudbuild/startup-scripts/
    gsutil cp $yamlpath gs://"$project"_cloudbuild/yaml-build-files/
    gsutil cp $introtocyberpath gs://"$project"_cloudbuild/yaml-build-files/
}

$confirmation = Read-Host "Do you want to update teacher and student workout instructions (for the primary UA Little Rock project only)? (y/N)"
if ($confirmation -eq 'y') {
    $confirmation = Read-Host "Do you want to first encrypt the teacher instructions in need of encryption? (y/N)"
    if ($confirmation -eq 'y') {
        $pass = Read-Host "What is the password you want to use for encryption? (Don't forget to use a double excalamation point for '!')"
        python password_protect_teacher_instructions.py -p $pass
    }
    $studentpath = Join-Path (Resolve-Path ..\).Path "\build-files\student-instructions\*.pdf"
    $teacherpath = Join-Path (Resolve-Path ..\).Path "\build-files\teacher-instructions\*.pdf"
    gsutil cp $studentpath gs://student_workout_instructions_tgd4419/
    gsutil cp $teacherpath gs://teacher_workout_instructions_84jf627/
}

$confirmation = Read-Host "Do you want to copy over ALL available cloud images? (y/N)"
if ($confirmation -eq 'y') {
    gcloud compute --project=$project images delete image-labentry
    gcloud compute --project=$project images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-account-control-v2
    gcloud compute --project=$project images create image-cybergym-account-control-v2 --source-image=image-cybergym-account-control-v2 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-activedirectory-domaincontroller
    gcloud compute --project=$project images create image-cybergym-activedirectory-domaincontroller --source-image=image-cybergym-activedirectory-domaincontroller --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-activedirectory-memberserver
    gcloud compute --project=$project images create image-cybergym-activedirectory-memberserver --source-image=image-cybergym-activedirectory-memberserver --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-arena-windows
    gcloud compute --project=$project images create image-cybergym-arena-windows --source-image=image-cybergym-arena-windows --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-arena-windows-3
    gcloud compute --project=$project images create image-cybergym-arena-windows-3 --source-image=image-cybergym-arena-windows-3 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-bufferoverflow
    gcloud compute --project=$project images create image-cybergym-bufferoverflow --source-image=image-cybergym-bufferoverflow--source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images create image-cybergym-cyberattack
    gcloud compute --project=$project images create image-cybergym-cyberattack --source-image=image-cybergym-cyberattack --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-forensics-workstation
    gcloud compute --project=$project images create image-cybergym-forensics-workstation --source-image=image-cybergym-forensics-workstation --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-fortinet-fortigate
    gcloud compute --project=$project images create image-cybergym-fortinet-fortigate --source-image=image-cybergym-fortinet-fortigate --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-hiddensite
    gcloud compute --project=$project images create image-cybergym-hiddensite --source-image=image-cybergym-hiddensite --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-nessus
    gcloud compute --project=$project images create image-cybergym-nessus --source-image=image-cybergym-nessus --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-nessus-arena
    gcloud compute --project=$project images create image-cybergym-nessus-arena --source-image=image-cybergym-nessus-arena --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-password-policy-v2
    gcloud compute --project=$project images create image-cybergym-password-policy-v2 --source-image=image-cybergym-password-policy-v2 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-ransomware
    gcloud compute --project=$project images create image-cybergym-ransomware --source-image=image-cybergym-ransomware --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-teenyweb
    gcloud compute --project=$project images create image-cybergym-teenyweb --source-image=image-cybergym-teenyweb --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-tiny-hiddentarget
    gcloud compute --project=$project images create image-cybergym-tiny-hiddentarget --source-image=image-cybergym-tiny-hiddentarget --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-vnc
    gcloud compute --project=$project images create image-cybergym-vnc --source-image=image-cybergym-vnc --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-wireshark
    gcloud compute --project=$project images create image-cybergym-wireshark --source-image=image-cybergym-wireshark --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-promise-attacker
    gcloud compute --project=$project images create image-promise-attacker --source-image=image-promise-attacker --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-promise-victim-win2012
    gcloud compute --project=$project images create image-promise-victim-win2012 --source-image=image-promise-victim-win2012 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-promise-vnc
    gcloud compute --project=$project images create image-promise-vnc --source-image=image-promise-vnc --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-promise-win-16
    gcloud compute --project=$project images create image-promise-win-16 --source-image=image-promise-win-16 --source-image-project=ualr-cybersecurity
    gcloud compute --project=$project images delete image-cybergym-activedirectory-domaincontroller
}

# Copy over only certain compute images
$confirmation = Read-Host "Do you want to copy over INDIVIDUAL cloud images? (y/N)"
if ($confirmation -eq 'y') {
    $images = Read-Host "  Provide a comma-separated list of images to copy over"
    foreach ($image in $images.Split(","))
    {
        gcloud compute --project $project images delete $image --quiet
        gcloud compute --project $project images create $image --source-image $image --source-image-project=ualr-cybersecurity
    }
}

# Copy over compute images for building workouts and arenas
$confirmation = Read-Host "Do you want to copy over machine-images at this time? (y/N)"
if ($confirmation -eq 'y')
{

    gcloud beta compute machine-images add-iam-policy-binding image-fortimanager --project = ualr-cybersecurity --member = serviceAccount: cybergym-service@$child_project.iam.gserviceaccount.com --role = roles/compute.admin`
    gcloud compute networks create cybergymfortinet-external-network --subnet-mode = custom
    gcloud compute networks subnets create cybergymfortinet-external-network-default --network = cybergymfortinet-external-network --range = 10.1.0.0/24
    gcloud compute networks create cybergymfortinet-dmz-network --subnet-mode = custom
    gcloud compute networks subnets create cybergymfortinet-dmz-network-default --network = cybergymfortinet-dmz-network --range = 10.1.2.0/24
    gcloud compute networks create cybergymfortinet-internal-network --subnet-mode = custom
    gcloud compute networks subnets create cybergymfortinet-internal-network-default --network = cybergymfortinet-internal-network --range = 10.1.1.0/24
    gcloud beta compute instances create cybergym-fortimanager --project = $child_project --zone us-central1-a --source-machine-image projects/ualr-cybersecurity/global/machineImages/image-fortimanager --service-account cybergym-service@$child_project.iam.gserviceaccount.com
    gcloud beta compute machine-images create image-fortimanager  --source-instance = cybergym-fortimanager  --source-instance-zone=us-central1-a
}
