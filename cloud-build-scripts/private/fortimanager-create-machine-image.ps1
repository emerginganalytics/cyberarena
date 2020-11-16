param (
    [string]$project = $( Read-Host "Input GCP project:" ),
    [string]$region = "us-central1"
 )

# Move to the correct project
gcloud config set project $project

gcloud beta compute machine-images add-iam-policy-binding image-fortimanager --project=ualr-cybersecurity --member=serviceAccount:cybergym-service@$project.iam.gserviceaccount.com --role=roles/compute.admin`

gcloud beta compute instances create cybergym-fortimanager --project=$project --zone us-central1-a --source-machine-image projects/ualr-cybersecurity/global/machineImages/image-fortimanager --service-account cybergym-service@trojan-cybergym.iam.gserviceaccount.com

gcloud beta compute machine-images create image-fortimanager  --source-instance=cybergym-fortimanager  --source-instance-zone=us-central1-a