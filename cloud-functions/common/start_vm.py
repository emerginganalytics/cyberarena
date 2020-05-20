def cloud_fn_start_vm(event,context):

    workout_id = event['attributes']['workout_id'] if 'workout_id' in event['attributes'] else None

    if not workout_id:
        if context:
            print("Invalid fields for pubsub message triggered by messageId{} published at {}".format(context.event_id, context.timestamp))
        return False
    
    
    print("Starting workout %s" % workout_id)
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout['running'] = True
    workout['start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(workout)

    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    try:
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().start(project=project, zone=zone, instance=vm_instance["name"]).execute()
                workout_globals.extended_wait(project, zone, response["id"])

                started_vm = compute.instances().get(project=project, zone=zone, instance=vm_instance["name"]).execute()
                if 'accessConfigs' in started_vm['networkInterfaces'][0]:
                    if 'natIP' in started_vm['networkInterfaces'][0]['accessConfigs'][0]:
                        tags = started_vm['tags']
                        if tags:
                            for item in tags['items']:
                                if item == 'labentry':
                                    ip_address = started_vm['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                                    register_workout_update(project, dnszone, workout_id, ip_address)
            time.sleep(30)
            print("Finished starting %s" % workout_id)
        return True
    except():
        print("Error in starting VM for %s" % workout_id)
        return False