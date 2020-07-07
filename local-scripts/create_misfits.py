from globals import ds_client, project, dnszone, compute


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
        workout['misfit'] = True
        ds_client.put(workout)


create_misfits('unit_id', '=', 'abenynrzka')