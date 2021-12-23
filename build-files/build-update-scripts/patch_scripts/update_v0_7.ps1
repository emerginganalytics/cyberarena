 param (
     [string]$project = $( Read-Host "Input GCP project:" )
 )
 $version = "0.7"

 gcloud config set project $project

 # Create cloud schedules
 $tz = Read-Host "What is your timezone? (America/Chicago) "
 if ($tz -eq '') {
     $tz = "America/Chicago"
 }
 gcloud scheduler jobs delete job-delete-expired-arenas --quiet
 gcloud scheduler jobs delete job-stop-lapsed-arenas --quiet
 gcloud scheduler jobs delete maint-del-job --quiet
 gcloud scheduler jobs delete stop-workouts --quiet
 gcloud scheduler jobs delete medic --quiet
 gcloud scheduler jobs delete job-delete-misfits --quiet

 gcloud scheduler jobs create pubsub job-delete-expired-arenas --schedule="0 * * * *" --topic=maint-del-tmp-systems --time-zone=$tz --message-body=Hello! --attributes=workout_type=arena
 gcloud scheduler jobs create pubsub job-stop-lapsed-arenas --schedule="*/15 * * * *" --topic=stop-lapsed-arenas --message-body=Hello!
 gcloud scheduler jobs create pubsub maint-del-job --schedule="0 * * * *" --topic=maint-del-tmp-systems --message-body=Hello! --attributes=workout_type=workout
 gcloud scheduler jobs create pubsub stop-workouts --schedule="*/15 * * * *" --topic=stop-workouts --message-body=Hello!
 gcloud scheduler jobs create pubsub medic --schedule="*/10 * * * *" --topic=medic --message-body=Fix-Workouts
 gcloud scheduler jobs create pubsub job-delete-misfits --schedule="0/15 * * * *" --topic=maint-del-tmp-systems --time-zone=$tz --message-body=Hello! --attributes=workout_type=misfit


 # At last, set the application version
 gcloud beta runtime-config configs variables set "version" $version --config-name "cybergym"