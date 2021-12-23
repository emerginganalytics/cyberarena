 param (
     [string]$project = $( Read-Host "Input GCP project:" ),
     [string]$admin_email = $( Read-Host "Provide an email address for the super administrator of this project:")
 )
 $version = "0.6"

 # Move to the correct project
 gcloud config set project $project

 $project_version = gcloud beta runtime-config configs variables get-value --config-name "cybergym" "version"

 # Create a super administrator for this project for default authorization
 gcloud beta runtime-config configs variables set "admin_email" $admin_email --config-name "cybergym"

 gcloud scheduler jobs delete maint-del-job
 gcloud scheduler jobs create pubsub maint-del-job --schedule="0 * * * *" --topic=maint-del-tmp-systems --message-body=Hello! --attributes=workout_type=workout
 gcloud scheduler jobs delete job-delete-expired-arenas
 gcloud scheduler jobs create pubsub job-delete-expired-arenas --schedule="0 * * * *" --topic=maint-del-tmp-systems --time-zone=$tz --message-body=Hello! --attributes=workout_type=arena
 gcloud scheduler jobs delete db-update
 gcloud scheduler jobs delete job-stop-all-servers
 gcloud scheduler jobs create pubsub job-daily_maintenance --schedule="0 0 * * *" --topic=daily_maintenance --message-body=Hello!

 gcloud functions delete function-delete-expired-arenas
 gcloud functions delete function-stop-all-servers
 gcloud functions delete function-db-update
 $sourcepath = Join-Path (Resolve-Path ..\).Path "\cloud-functions"
 gcloud functions deploy --quiet function-delete-expired-workouts `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_delete_expired_workout `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=maint-del-tmp-systems
 gcloud functions deploy --quiet function-daily-maintenance `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_daily_maintenance `
        --runtime=python37 `
        --source=$sourcepath `
        --timeout=540s `
        --trigger-topic=daily_maintenance
 gcloud functions deploy --quiet function-manage-server `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_manage_server `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=manage-server
 gcloud functions deploy --quiet function-medic `
        --region=$region `
        --memory=256MB `
        --entry-point=cloud_fn_medic `
        --runtime=python37 `
        --source=$sourcepath `
        --service-account=cybergym-service@"$project".iam.gserviceaccount.com `
        --timeout=540s `
        --trigger-topic=medic

 # At last, set the application version
 gcloud beta runtime-config configs variables set "version" $version --config-name "cybergym"
