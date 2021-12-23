from common.globals import ds_client

def extend_expiration_unit(unit_id, days):
    """
    Extend the number of days before the workout automatically expires for a given unit.
    :param unit_id: The unit_id
    :param days: Number of days to extend for the unit
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    for workout in list(query_workouts.fetch()):
        current_expiration = int(workout['expiration'])
        workout['expiration'] = f"{current_expiration + days}"
        ds_client.put(workout)
