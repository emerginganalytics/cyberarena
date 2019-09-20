
def body_workout_message(workout_type, team_url):
    print(workout_type)

    if (workout_type == "cyberattack"):
        message = "Welcome to your team's cyber attack workout, in which you will experience how a cyber-attack known as a botnet works. Your server should be ready at the following website: {}".format(team_url)
    
    if (workout_type == "dos"):
        message = "Test dos message workout {}".format(team_url)

    if (workout_type == "phishing"):
        message = "Welcome to your team's phishing workout in which you will learn how a phishing attack works and how to do avoid them. Your server should be ready at the following website: {}".format(team_url)

    if (workout_type == "theharbor"):
        message = "Welcome to TheHarbor! Here you will learn a brief demonstration of a firewall at work. Block the correct ports and you might find a flag hidden in the site. You server should be ready at the following website: {}".format(team_url)

    return message


