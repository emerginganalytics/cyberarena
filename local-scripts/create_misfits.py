from utilities.globals import ds_client


def create_misfits(field, operator, filter):
    """
    Set the misfit field to True for all workouts and arenas matching the filter. This will
    ensure these workouts get picked up for deletion.
    :param field: The datastore field to filter on.
    :param operator: The operator to use (i.e. <, >, =)
    :param filter: The filter to apply
    :return: None
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter(field, operator, filter)
    for workout in list(query_workouts.fetch()):
        if int(workout['timestamp']) > 1593959440:
            #workout['misfit'] = True
            workout['expiration'] = 1
            ds_client.put(workout)


create_misfits('type', '=', 'mobileforensics')