"""
Create method to add user to the database
add prompt for user email
add prompt to set permissions admin, instructor, student
"""

from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer


def main():
    user = str(input("Enter user email: "))
    admin = input("Admin? (y/N: ")
    if admin.upper() == "N":
        admin = False
    else:
        admin = True
    instructor = input("Instructor? (y/N): ")
    if instructor.upper() == "N":
        instructor = False
    else:
        instructor = True
    student = input("Student? (Y/n): ")
    if student.upper() == "N":
        student = False
    else:
        student = True
    ArenaAuthorizer().add_user(email=user, admin=admin, instructor=instructor, student=student)


if __name__ == '__main__':
    main()



"""
def add_user():
    ArenaAuthorizer().add_user(email=user, admin=admin, instructor=instructor, student=student)
"""


"""
def add_user():
    ArenaAuthorizer().add_user(email=str('your email'), admin=True, instructor=True, student=True)
"""


