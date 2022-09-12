from v2.main_app.main_app_utilities.gcp.datastore_manager import DataStoreManager


def hours_from_sec(seconds):
    return int(seconds / 60 / 60)


def get_workout_stats(workout_name):
    query = DataStoreManager(key_id='cybergym-workout').query()
    query.add_filter('type', '=', str(workout_name))
    query_list = list(query.fetch())

    print(f'{workout_name.upper()} Workout Stats\n-------------------------------')

    total_hours = 0
    count = 0
    total_builds = len(query_list)
    highest_rt = 0
    visted = []
    hour_counts = []
    hours_list = []
    for workout in query_list:
        runtime_counter = workout.get('runtime_counter', None)
        if runtime_counter:
            hours = hours_from_sec(runtime_counter)
            if hours > 0:
                if hours > highest_rt:
                    highest_rt = hours
                hours_list.append(hours)
                count += 1
                total_hours += hours
                print(f'{hours}')
            else:
                total_builds -= 1
        else:
            total_builds -= 1

    hours_list.sort()
    for hour in hours_list:
        if hour not in visted:
            hour_counts.append(f'{hour} hour/s appeared {hours_list.count(hour)} times')
            visted.append(hour)
        continue

    print('-------------------------------------------')
    print(f'Total Built: {total_builds}')
    print(f'Total Hours: {total_hours}')
    print(f'Average Hours: {total_hours / total_builds}')
    print(f'Largest Runtime: {highest_rt}')
    print('-------------------------------------------')
    for hour in hour_counts:
        print(hour)


if __name__ == '__main__':
    workout_name = input('[+] Enter workout name ::')
    get_workout_stats(workout_name)