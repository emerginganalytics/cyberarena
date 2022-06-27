import argparse
from common.globals import ds_client
from google.cloud import datastore


def assign_instructor_to_unit(unit_id, prev_instructor, instructor_email):
    """
    Replaces existing instructor in unit with the email provided.
    Useful in cases where admins need to create a unit and assign it
    to instructors at a later date.

    This is a temporary solution until a more elegant method is developed
    :@param unit_id:
    :@param instructor_email:
    """
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    workout_list = list(query_workouts.fetch())

    # Update workout Instructor Email
    for workout in workout_list:
        print(f'[*] Updating instructor for workout, {workout.key.name} ...')
        workout['instructor_email'] = instructor_email
        ds_client.put(workout)

    # Update Unit Instructor Email
    print(f'[*] Updating unit ({unit_id}) instructor from {unit["instructor_id"]} to {instructor_email} ...')
    unit['instructor_id'] = instructor_email
    ds_client.put(unit)

    # Transfer unit to new class with instructor_email as the new teacher_email
    query_class = ds_client.query(kind='cybergym-class')
    query_class.add_filter('teacher_email', '=', prev_instructor)
    class_list = list(query_class.fetch())

    # TODO: Look into ways of checking if class with exact roster already exists for an instructor and simply adding the
    #       unit to that class instead of creating a whole new class each time.
    remove_unit = ''
    for class_obj in class_list:
        current_list = class_obj.get('unit_list', None)
        if current_list:
            for current_unit in current_list:
                if unit_id == current_unit['unit_id']:
                    print('[*] Creating new class for unit ...')
                    # Copy unit over to new instructor class
                    new_class = datastore.Entity(ds_client.key('cybergym-class'))
                    new_class['roster'] = class_obj['roster']
                    new_class['student_auth'] = class_obj['student_auth']
                    new_class['class_name'] = class_obj['class_name']
                    new_class['teacher_email'] = instructor_email
                    new_class['unit_list'] = [current_unit,]
                    ds_client.put(new_class)

                    # Grab class values that we need to update
                    remove_unit = current_unit
                    break
        if remove_unit:
            print('[*] Removing unit from old class ...')
            class_obj['unit_list'].remove(remove_unit)
            ds_client.put(class_obj)
            break
    print('[+] done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unit', required=True, help="Unit_id of Unit that needs reassigned")
    parser.add_argument('-n', '--new', required=True, help='Email of instructor to assign the unit to')
    parser.add_argument('-p', '--previous', required=True, help='Email of Instructor the unit is currently assigned to')
    args = parser.parse_args()

    assign_instructor_to_unit(unit_id=args.unit, prev_instructor=args.previous,
                              instructor_email=args.new)
