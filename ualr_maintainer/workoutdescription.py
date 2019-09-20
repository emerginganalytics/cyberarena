
def body_workout_message(workout_type, team_url):
    print(workout_type)

    email_body_header = ' '
    email_body_header += '<html><head></head><body>'
    email_body_header += '<style type="text/css"></style>'

    if (workout_type == "cyberattack"):
        email_body_content = " "
        email_body_content += "<h1>The Cyber Attack Workout</h1>"
        email_body_content += "Welcome to your team's cyber attack workout, in which you will experience how a " \
                                "cyber-attack known as a botnet. Your server should now be ready at the following " \
                                "website: {}".format(team_url)
        email_body_content += '<h2>Preparation:</h2> ' \
                  '<ol style=""> ' \
                    '<li style="">Log into the Guacamole web server using <i>init_user</i> and ' \
                        '<i>promiseme</i> as the username and password.</li>' \
                    '<li style="">You may have to refresh the page if a screen does not come up.</li>' \
                    '<li style="">Once you are logged in, double click shinobot to run it.</li>' \
                    '<li style="">In another tab, browse to ' \
                        '<a href="http://shinobotps1.com/">http://shinobotps1.com</a>/ and click on ' \
                        'the C&amp;C tab.</li><li style="">Find your instance and login with the ' \
                        'credentials 5xvoKbVlGegt.</li></ol>' \
                  '<h2>Exercises:</h2>' \
                  '<ol style="">' \
                    '<li style="">On the shinobot C&amp;C, scroll down until you see the ' \
                        'command prompt. Type in the following command: "<b>calc.exe</b>" ' \
                        'without the quotes. After inputting the command, switch back to the windows' \
                        'screen and notice how the calculator has now opened up. (Note: You may have' \
                        'to wait a few seconds before the command is processed.)</li>' \
                    '<li style="">Now, scroll down a little bit more to see something titled ' \
                        '<b>command template</b> and a drop down menu that says select category. ' \
                        'Let us start by clicking on the menu and selecting List Up All Windows User. ' \
                        'After a few seconds, you should see output that displays all available user accounts.</li>' \
                    '<li style="">Now, let\'s choose the system category. Click any of the choices and ' \
                        'see what kind of output it gives you. This is how an attacker would begin ' \
                        'gathering information on a potential target.</li>' \
                    '<li style="">What if you wanted to see the victim\'s desktop? Use the ' \
                        '"<span style="font-weight: bold;">Take Screenshot</span>" option to accomplish this.</li>' \
                    '<li style="">Finally, let\'s try to harvest some credentials. Browse to a site called ' \
                        '<a href="http://aavtrain.com" target="" title="">aavtrain.com</a> ' \
                        'where you\'ll be greeted with a login prompt. Put in some fake credentials like ' \
                        'the following:<br>User: iamatest<br>Password: thisisatest<br> ' \
                        'Now, in the shinobot C&amp;C, go to the command template, and choose the' \
                        ' credentials category. Choose the "Get credentials from browser" option and you ' \
                        'should get an output with the username and password you entered. Note: If for some' \
                        ' reason you don\'t receive any output, try clearing all browser history.</li></ol>'

    elif (workout_type == "dos"):
        email_body_content = " "
        email_body_content += "<h1>DOS Workout</h1>"
        email_body_content += "Welcome to your team's Denial of Service workout, in which you will experience how a " \
                                "Denial of Service attack works. Your server should now be ready at the following " \
                                "website: {}".format(team_url)
    elif (workout_type == "phishing"):
        email_body_content = " "
        email_body_content += "<h1>Phishing Workout</h1>"
        email_body_content += "Welcome to your team's phishing workout, in which you will experience how a " \
                                "phishing attack works. Your server should now be ready at the following " \
                                "website: {}".format(team_url)


    email_body_footer = ' '
    email_body_footer = email_body_footer + '<br>Thank you'
    email_body_footer = email_body_footer + '<br>Your Cyber Gym Support Team<br>' \
                                            '<br>cybergym@ualr.edu</body></html>'

    email_body = str(email_body_header) + str(email_body_content) + str(email_body_footer)

    return email_body
>>>>>>> f0158763c716587f0b921d3cef2b4eadf54853da


