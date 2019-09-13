
def body_workout_message(workout_type, team_url):
    print(workout_type)

    if (workout_type == "cyberattack"):
        message = "Welcome to your team's cyber attack workout, in which you will experience how a cyber-attack known as a botnet. Your server should be ready at the following website: {}".format(team_url)
    
    if (workout_type == "dos"):
        message = "Test dos message workout {}".format(team_url)

    return message


