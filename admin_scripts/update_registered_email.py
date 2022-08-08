import click
from google.cloud import datastore

@click.command()
@click.argument('class_name')
@click.argument('curr_email')
@click.argument('new_email')
def update_registered_email(class_name, curr_email, new_email):
    """
    Updates student email for all assigned workouts. Intended for cases where
    student was registered in a class under an incorrect email address.
    :param class_name: Name of the class we want to update student email in
    :param curr_email: Email we want to update
    :param new_email:  Email we want to update with
    """
    # Query target class
    ds_client = datastore.Client(project='')
    cybergym_class = ds_client.query(kind='cybergym-class')
    cybergym_class.add_filter('class_name', '=', class_name)
    cybergym_class_list = list(cybergym_class.fetch())

    new_email = new_email.lower()

    # Update class roster
    for classes in cybergym_class_list:
        for student in classes['roster']:
            if student['student_email'] == curr_email:
                print(f'[+] Update class roster with {new_email}')
                student['student_email'] = new_email
                ds_client.put(classes)
                break

    # Update all workouts for curr_email
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('student_email', '=', curr_email)
    for workout in list(query_workouts.fetch()):
        workout['student_email'] = new_email
        print(f'[*] Updating workout\'s student_email with {new_email}')
        ds_client.put(workout)

    # Finally, replace current email with new email in authed students list
    query_auth_users = ds_client.query(kind='cybergym-admin-info')
    for students in list(query_auth_users.fetch()):
        for pos, student in enumerate(students['students']):
            if student == curr_email:
                students['students'][pos] = new_email
                print(f'[+] Replaced {curr_email} with {students["students"][pos]} in authed users list')
                ds_client.put(students)
                break

    print('[+] Update complete!')


if __name__ == '__main__':
    update_registered_email()
