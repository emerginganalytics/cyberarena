#!/bin/bash
#
#Note: If you're on Windows, you need to install Bash and gcloud for this to run. 
#
#Once gcloud is installed, make sure you're on the right project (nsa-healthcare)
#
#This script is meant to be used in cases where virtual machine instances do not have nested virtualization enabled. 
#
#
#

INSTANCES=( $(gcloud compute instances list --format="table(name)" | grep "metasploitable") )

ZONE="us-central1-a"

for ELEMENT in ${INSTANCES[@]}
do 
    echo $ELEMENT
    echo "Instance exists!"
    gcloud compute instances export $ELEMENT --destination=$ELEMENT.yaml --zone=$ZONE

    if ! grep -q enableNestedVirtualization "$ELEMENT.yaml";then
        echo "Nested virtualization not enabled! Enabling now.."
        echo "advancedMachineFeatures:" >> $ELEMENT.yaml
        echo "  enableNestedVirtualization: true" >> $ELEMENT.yaml

        gcloud compute instances update-from-file $ELEMENT --source=$ELEMENT.yaml --most-disruptive-allowed-action=RESTART --zone=$ZONE
        rm $ELEMENT.yaml
    else
        echo "Nested virtualization is already enabled!"
        rm $ELEMENT.yaml
    fi

done
