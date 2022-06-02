from google.cloud import storage
import secrets
import os.path
import subprocess

project_name = str(input(f"Input GCP project: "))
region = str("us-central1")


# Move to the correct project
subprocess.call("gcloud config set project" + project_name, shell=True)

# Update the main application
confirmation = str(input("Do you want to update the main applications? (y/N): "))
if (confirmation == 'y'):
    app = str(input("What is the application name? (cybergym): "))
    if (app == 'y'):
        app = "cybergym"
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\main")
subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / " + app, shell=True)
subprocess.call("gcloud run deploy " + app + " --image gcr.io / " + project_name + " / " + app + " --memory=1024Mi --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update cybergym-classified
confirmation = str(input("Do you want to update cybergym-classified? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath =  os.path.join(os.path.normpath(path), r"\container-applications\classified")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / cybergym-classified", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / cybergym-classified --memory=256 --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update Shodan
confirmation = str(input("Do you want to update cybergym-shodanlite? (y/N): "))
if (confirmation == 'y'):
    shodan_api_key = str(input("Input the Shodan API Key: " ))
    subprocess.call("gcloud beta runtime-config configs variables set 'SHODAN_API_KEY' " + shodan_api_key + " --config-name 'cybergym'", shell=True)
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\Shodan")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / cybergym-shodanlite", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / cybergym-shodanlite --memory=256 --platform=managed --region=" + region + "  --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update Arena Snake
confirmation = str(input("Do you want to update Arena Snake? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\Arena Snake")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / arena-snake-loader", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / arena-snake-loader --memory=256 --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update JohnnyHash
confirmation = str(input("Do you want to update Johnny Hash Crypto Server? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\JohnnyHash")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / cryptoserver", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / cryptoserver --memory=256Mi --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


confirmation = str(input("Do you want to update IoT webserver? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\IoT")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / nsa-healthcare", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / nsa-healthcare --memory=256Mi --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update vulnerability_defender
confirmation = str(input("Do you want to update Vulnerability Defender? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\vulnerability-defender")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / vulnerability-defender", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / vulnerability-defender --memory=256 --platform=managed --region=" + region + " --allow-unauthenticated --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Update the Capability Maturity Model Assessment
confirmation = str(input("Do you want to update the CMMC assessment? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\container-applications\Assessment-Form")
    subprocess.call("gcloud builds submit " + sourcepath + " --tag gcr.io / " + project_name + " / cmmc-assessment", shell=True)
    subprocess.call("gcloud run deploy --image gcr.io / " + project_name + " / cmmc-assessment --memory=512 --platform=managed --region=" + region + " --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com", shell=True)


# Create the cloud functions
confirmation = str(input("Do you want to update ALL cloud functions? (y/N): "))
if (confirmation == 'y'):
    path = r'..\\'
    sourcepath = os.path.join(os.path.normpath(path), r"\cloud-functions")
    subprocess.call("gcloud functions deploy --quiet function-build-arena --region=" + region + " --memory=256MB --entry-point=cloud_fn_build_arena --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=build_arena", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-build-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_build_workout --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=build-workouts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-delete-expired-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_delete_expired_workout --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=maint- del -tmp-systems", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-manage-server --region=" + region + " --memory=256MB --entry-point=cloud_fn_manage_server --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=manage-server", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-start-arena --region=" + region + " --memory=256MB --entry-point=cloud_fn_start_arena --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=start-arena", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-start-vm --region=" + region + " --memory=256MB --entry-point=cloud_fn_start_vm --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=start-vm", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-lapsed-arenas --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_lapsed_arenas --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=stop-lapsed-arenas", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-lapsed-workouts --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_lapsed_workouts --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=stop-workouts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-stop-vm --region=" + region + " --memory=256MB --entry-point=cloud_fn_stop_vm --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=stop-vm", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-medic --region=" + region + " --memory=256MB --entry-point=cloud_fn_medic --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=medic", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-iot-capture-sensor --region=" + region + " --memory=256MB --entry-point=cloud_fn_iot_capture_sensor --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=cybergym-telemetry", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-admin-scripts --region=" + region + " --memory=256MB --entry-point=cloud_fn_admin_scripts --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=admin-scripts", shell=True)
    subprocess.call("gcloud functions deploy --quiet function-budget-manager --region=" + region + " --memory=256MB --entry-point=cloud_fn_budget_manager --runtime=python37 --source=" + sourcepath + " --service-account=cybergym-service @ " + project_name + ".iam.gserviceaccount.com --timeout=540s --trigger-topic=budget", shell=True)


confirmation = str(input("Do you want to update INDIVIDUAL cloud functions? (y/N): "))
if (confirmation == 'y'):
    while True:
        function = str(input("  Which function would you like to update?"))
        entry = str(input("  What is the entry-point function?"))
        topic = str(input("  What is the pub-sub-topic?"))
        path = r'..\\'
        sourcepath = os.path.join(os.path.normpath(path), r"\cloud-functions")
        subprocess.call("gcloud functions deploy --quiet " + function + " --region=" + region + " --memory=256MB --entry-point=" + entry + " --runtime=python37 --source=" + sourcepath + " --timeout=540s --trigger-topic=" + topic, shell=True)
        confirmation = str(input("Do you want to update any more cloud functions? (y/N)"))
        if (confirmation == 'N'):
            break


confirmation = str(input("Do you want to update build yaml specifications and startup scripts? (y/N): "))
if (confirmation == 'y'):
    path = r'\\'
    yamlpath = os.path.join(os.path.normpath(path), r"\build-files\*.yaml")
    introtocyberpath = os.path.join(os.path.normpath(path), r"\build-files\intro-to-cyber\*.yaml")
    scriptpath = os.path.join(os.path.normpath(path), r"\build-files\startup-scripts\*")
    subprocess.call("gsutil cp " + scriptpath + " gs://" + project_name + "_cloudbuild/startup-scripts/", shell=True)
    subprocess.call("gsutil cp " + yamlpath + " gs://" + project_name + "_cloudbuild/yaml-build-files/", shell=True)
    subprocess.call("gsutil cp " + introtocyberpath + " gs://" + project_name + "_cloudbuild/yaml-build-files/", shell=True)


confirmation = str(input("Do you want to update teacher and student workout instructions (for the primary UA Little Rock project only)? (y/N): "))
if (confirmation == 'y'):
    confirmation = str(input("Do you want to first encrypt the teacher instructions in need of encryption? (y/N): "))
    if (confirmation == 'y'):
        password = str(input("What is the password you want to use for encryption? (Don't forget to use a double excalamation point for '!'): "))
        subprocess.call("python password_protect_teacher_instructions.py -p" + password)
    path = r'\\'
    studentpath = os.path.join(os.path.normpath(path), r"\build-files\student-instructions\*.pdf")
    teacherpath = os.path.join(os.path.normpath(path), r"\build-files\teacher-instructions\*.pdf")
    subprocess.call("gsutil cp " + studentpath + " gs://student_workout_instructions_tgd4419/", shell=True)
    subprocess.call("gsutil cp " + teacherpath + " gs://teacher_workout_instructions_84jf627/", shell=True)


confirmation = str(input("Do you want to copy over ALL available cloud images? (y/N): "))
if (confirmation == 'y'):
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-labentry", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-labentry --source-image=image-labentry --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-account-control-v2", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-account-control-v2 --source-image=image-cybergym-account-control-v2 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-activedirectory-domaincontroller", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-activedirectory-domaincontroller --source-image=image-cybergym-activedirectory-domaincontroller --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-activedirectory-memberserver", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-activedirectory-memberserver --source-image=image-cybergym-activedirectory-memberserver --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-arena-windows", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-arena-windows --source-image=image-cybergym-arena-windows --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-arena-windows-3", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-arena-windows-3 --source-image=image-cybergym-arena-windows-3 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-bufferoverflow", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-bufferoverflow --source-image=image-cybergym-bufferoverflow--source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-cyberattack", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-cyberattack --source-image=image-cybergym-cyberattack --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-forensics-workstation", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-forensics-workstation --source-image=image-cybergym-forensics-workstation --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-fortinet-fortigate", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-fortinet-fortigate --source-image=image-cybergym-fortinet-fortigate --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-hiddensite", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-hiddensite --source-image=image-cybergym-hiddensite --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-nessus", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-nessus --source-image=image-cybergym-nessus --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-nessus-arena", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-nessus-arena --source-image=image-cybergym-nessus-arena --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-password-policy-v2", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-password-policy-v2 --source-image=image-cybergym-password-policy-v2 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-ransomware", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-ransomware --source-image=image-cybergym-ransomware --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-teenyweb", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-teenyweb --source-image=image-cybergym-teenyweb --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-tiny-hiddentarget", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-tiny-hiddentarget --source-image=image-cybergym-tiny-hiddentarget --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-vnc", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-vnc --source-image=image-cybergym-vnc --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-wireshark", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-cybergym-wireshark --source-image=image-cybergym-wireshark --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-promise-attacker", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-attacker --source-image=image-promise-attacker --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-promise-victim-win2012", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-victim-win2012 --source-image=image-promise-victim-win2012 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-promise-vnc", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-vnc --source-image=image-promise-vnc --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-promise-win-16", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images create image-promise-win-16 --source-image=image-promise-win-16 --source-image-project=ualr-cybersecurity", shell=True)
    subprocess.call("gcloud compute --project=" + project_name + " images delete image-cybergym-activedirectory-domaincontroller", shell=True)


# Copy over only certain compute images
confirmation = str(input("Do you want to copy over INDIVIDUAL cloud images? (y/N): "))
if (confirmation == 'y'):
    images = str(input("  Provide a comma-separated list of images to copy over (no spaces): "))
    for image in images.split(","):
        subprocess.call("gcloud compute --project " + project_name + " images delete " + image + " --quiet", shell=True)
        subprocess.call("gcloud compute --project " + project_name + " images create " + image + " --source-image " + image + " --source-image-project=ualr-cybersecurity", shell=True)


# Copy over compute images for building workouts and arenas
confirmation = str(input("Do you want to copy over machine-images at this time? (y/N): "))
if (confirmation == 'y'):

    subprocess.call("gcloud beta compute machine-images add-iam-policy-binding image-fortimanager --project = ualr-cybersecurity --member = serviceAccount: cybergym-service@" + child_project + ".iam.gserviceaccount.com --role = roles/compute.admin`", shell=True)
    subprocess.call("gcloud compute networks create cybergymfortinet-external-network --subnet-mode = custom", shell=True)
    subprocess.call("gcloud compute networks subnets create cybergymfortinet-external-network-default --network = cybergymfortinet-external-network --range = 10.1.0.0/24", shell=True)
    subprocess.call("gcloud compute networks create cybergymfortinet-dmz-network --subnet-mode = custom", shell=True)
    subprocess.call("gcloud compute networks subnets create cybergymfortinet-dmz-network-default --network = cybergymfortinet-dmz-network --range = 10.1.2.0/24", shell=True)
    subprocess.call("gcloud compute networks create cybergymfortinet-internal-network --subnet-mode = custom", shell=True)
    subprocess.call("gcloud compute networks subnets create cybergymfortinet-internal-network-default --network = cybergymfortinet-internal-network --range = 10.1.1.0/24", shell=True)
    subprocess.call("gcloud beta compute instances create cybergym-fortimanager --project = " + child_project + " --zone us-central1-a --source-machine-image projects/ualr-cybersecurity/global/machineImages/image-fortimanager --service-account cybergym-service@" + child_project + ".iam.gserviceaccount.com", shell=True)
    subprocess.call("gcloud beta compute machine-images create image-fortimanager  --source-instance = cybergym-fortimanager  --source-instance-zone=us-central1-a", shell=True)
