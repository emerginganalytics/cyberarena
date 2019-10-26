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
    elif (workout_type == "xss"):
        email_body_content = " "
        email_body_content += "<h1>Cross-Site Scripting Workout</h1>"
        email_body_content += "Welcome to your team's cross-site scripting workout! " \
                                "website: {}".format(team_url)
    elif (workout_type == "dos"):
        email_body_content = " "
        email_body_content += "<h1>DoS Workout</h1>"
        email_body_content += "Welcome to your team's Denial of Service workout, in which you will experience how a " \
                                "Denial of Service attack works. Your server should now be ready at the following " \
                                "website: {}".format(team_url)
        email_body_content += '<h2>Preparation:</h2> ' \
                              '<ol> ' \
                    '<li>Log into the Guacamole web server using <i>init_user</i> and ' \
                        '<i>promiseme</i> as the username and password.</li>' \
                    '<li>You may have to refresh the page if a screen does not come up.</li></ol>' \
                  '<h2>Attacker:</h2>' \
                  '<ol>' \
                    '<li>Open the terminal from applications and enter&#10;cd /loic/LOIC/&#10;./loic.sh run</li>'\
                    '<li> You should see the Low Orbital Ion Cannon application window open. In the IP input' \
                    'form enter 10.1.1.3 and click the Lock On button. <b>Do not change any other setting.</b>' \
                              ' When you are ready click the ready button to start dosing the defender VM</li>' \
                    '</ol>' \
                  '<h2>Defender:</h2>' \
                  '<ol>' \
                    '<li>Click the top left button named Applications. Hover down to the Systems Tools tab and click' \
                              'the System Monitor tool. Within the tool, click the Resources tab. You will see the' \
                              ' CPU history. This is important to monitor when experiencing the DoS attack. </li>' \
                '</ol>'
    elif (workout_type == "phishing"):
        email_body_content = " "
        email_body_content += "<h1>Phishing Workout</h1>"
        email_body_content += "Welcome to your team's phishing workout, in which you will experience how a " \
                                "phishing attack works. Your server should now be ready at the following " \
                                "website: {}".format(team_url)

    elif (workout_type == "hiddennode"):
        email_body_content = " "
        email_body_content += "<h1>Hidden Node Workout</h1>"
        email_body_content += "Welcome to your team's hidden node workout. Here you will use basic recon tactics to " \ 
                              'discover a node hidden in the network. Your server should now be ready at the ' \
                              'following website: {}'.format(team_url)
        email_body_content += '<div class="yui-wk-div"><span style="white-space: pre;"><span style="font-weight: ' \
                              'bold;">Preparation:</span><span style="font-weight: 700;"></span><ul style="">' \
                              '<li style=""><span style="white-space: pre;">Log into the Guacamole web server using ' \
                              '</span><i style="white-space: pre;">init_user</i><span style="white-space: pre;"> and ' \
                              '</span><i style="white-space: pre;">promiseme</i><span style="white-space: pre;"> as ' \
                              'the username and password.</span></li></ul></span></div><br><br>1.&nbsp; Open the ' \
                              'Zenmap application on your machine.<br><ul>'\
                              '<li>To open Zenmap, go to <span style="font-weight: 700;">Applications &lt; Internet '\
                              '&lt; Zenmap (run as root)<br></span></li><li>Enter the same password&nbsp; as above '\
                              'to run the program as root.</li></ul><br><br>2. In the input box type in the following '\
                              'code<br><gcb-code mode="" instanceid="RS81NILI6rpx">nmap -sn -T5 10.1.0.0/24</gcb-code>'\
                              '<br>The command -sn allows you scan a range of IP address to see if they are up and '\
                              '-T5 tells Zenmap how aggressive to scan with five being the loudest in a network.<br>'\
                              '10.1.0.0/24 is the range of IP address from 10.1.1.0 - 10.1.1.255<br><br>3. When you '\
                              'run it you will see five different IP address<br>10.1.1.10 is our IP address.'\
                              '<br>10.1.1.1 is not important to this workout.<br>This leaves three machines left. '\
                              'Try running a basic scan against each of the remaining three IP addresses.&nbsp;<br>'\
                              '<br><br>4. Type the following code into the input box. Each new line will run a new '\
                              'target scan so be sure to wait <br>until the current scan is finished before beginning '\
                              'a new one.<br><gcb-code mode="" instanceid="UHqsG475vUN5">nmap 10.1.1.111 nmap '\
                              '10.1.1.115 nmap 10.1.1.253 </gcb-code><br>Remember, be sure to record the open ports '\
                              'for each scan before scanning the next target.<br><br>5. If you scan the targets in '\
                              'the order listed you will find the first two targets only have one open port each, 22 '\
                              'and 3389.<br>Port 22 is the port number used for SSH connections and 3389 is used for '\
                              "RDP. For now, we aren't interested in these ports.<br>The last machine, 10.1.1.253 "\
                              'will return four total ports<br><ul><li>22 (SSH)</li><li>80 (HTTP)</li><li>5901 (VNC)'\
                              "</li><li>6001&nbsp; (X11)</li></ul><div>Again, we aren't interested in port 22. Ports "\
                              '5901 and 6001 are how you are able to connect to graphical interface.&nbsp;<br>This '\
                              'leaves port 80 which is the default port used for web access.</div>'\
                              '<br><br>6. Go to 10.1.1.253 in the web browser and record what you find.'

    elif (workout_type == "shodan"):
        email_body_content = " " 
        email_body_content += "<h1>Shodan Search Engine</h1>"
        email_body_content += "Welcome to the Shodan exercise, where you will learn how to find and search up IoT " \
                              "devices and other systems across the       Internet.&nbsp;<br><br>When using the " \
                              "Shodan search engine, here are some search terms:<br><ul>" \
                              "<li>port:554 has_screenshot:true</li><li>category:malware</li>" \
                              "<li>port:25565</li><li>gps</li></ul><div>Try messing around with the search terms and " \
                              "look up common IoT devices like fridges, microwaves, etc.<br>" \
                              "Link:<a href='https://www.shodan.io/'>https://www.shodan.io</a><br></div>"

    elif (workout_type == "BinaryHex"):
        email_body_content = " "
        email_body_content += "<h1>Binary and Hex Games</h1>"
        email_body_content += "Welcome to the binary and hex games! These games will both teach you the fundamentals " \
                              "of binary and hexadecimal which are essential to   learning about other topics like " \
                              "reverse engineering and binary exploitation. Follow the additional instructions each " \
                              "game provides and have fun." \
                              "<br>Links:<br>BinaryBlitz:<a href='https://games.penjee.com/binary-numbers-game/'> " \
                              "https://games.penjee.com/binary-numbers-game/</a><br>FlippyBit:" \
                              "<a href='http://flippybitandtheattackofthehexadecimalsfrombase16.com/'>"\
                              "http://flippybitandtheattackofthehexadecimalsfrombase16.com/</a>&nbsp;"

    elif (workout_type == "osint"):
        email_body_content = " "
        email_body_content += "Welcome to the OSINT challenge! You've been given the task of gathering information on "\
                              "an individual known as Thomas Atkins. He is a senior software analyst at TechHex. The "\
                              "information you gather from him should eventually lead you to a flag. Hint: Start by "\
                              "looking at LinkedIn."

    elif (workout_type == "hashmyfiles"):
        email_body_content = " "
        email_body_content += "<h1>Hash My Files</h1>"
        email_body_content += "Welcome to your team's hashing workout. Here you will discover the importance of " \
                              "reading file hashes. Your server should be ready at the following " \
                              "website: {}".format(team_url)
        email_body_content += "<br><br><span style='font-weight: 700; text-decoration-line: underline;'> " \
                              "Objective of the Lab:</span><br>For this workout, we will be using the Windows Server " \
                              "2016 Virtual Machine. The workouts are stored in a folder called Crypto Labs. This " \
                              "time, we will be using the program, HashMyFiles, to check if each MD5 hash of the " \
                              "lab files are the same as the one's provided in the lab.<br><br>" \
                              '<span style="font-weight: bold; text-decoration-line: underline;">MD5 Hashes: ' \
                              "</span>&nbsp;<br><div class='yui-wk-div'>junk1:756edf02e845e9ea432caaad4b6a48b6" \
                              "</div><div class='yui-wk-div'>junk2:cfbaf687c9ccc5ae41b483f4f4158eda</div> " \
                              "<div class='yui-wk-div'>junk3:77c7b4017439256042775724a3281af5</div> " \
                              '<div class="yui-wk-div">junk4:fbf5bca33521752656f7acacbf93c51c</div> ' \
                              '<div class="yui-wk-div">junk5:ab08a62b4042fa833573172a67944bf1</div> ' \
                              '<div class="yui-wk-div">junk6:123e09403dacc9bf1091e1ad340ad80f</div> ' \
                              '<div class="yui-wk-div">junk7:a02f5ea2cf85c7efd91937d8837e283e</div> ' \
                              '<div class="yui-wk-div">junk8:c74c56db1adcb161f208b67854b2a2ce<br><br>1) Inside ' \
                              "the folder called Hashing Labs, there are 8 text files called junk.txt. Which one " \
                              "of these files are holding the flag? It would be good to know that one of the files " \
                              "has been tampered with recently. To check for recent file changes, we need to check " \
                              'the file hashes. Start by opening up HashMyFiles.<br>' \
                              '<img src="assets/img/Selection_085.png"class="yui-img" title="" alt=""><br><br>2) ' \
                              "With HashMyFiles open, click on File and choose the option that says add files. Make " \
                              "sure to add every 'junk(*).txt' file. Once that's finished, one should see each file's "\
                              "value displayed on the right. For now, only concentrate on the MD5 hashes.&nbsp;<br> " \
                              '<img src="assets/img/Selection_086.png" class="yui-img" title="" alt=""><br><br>3) ' \
                              "Now, try and validate each hash value with the values given in the directions above. " \
                              "If the values are the same, then the file has not been tampered with. If the values " \
                              "are different, then something has been changed. Notice how junk5.txt has a different " \
                              'value. This must be the flag!<br><img src="assets/img/Selection_087.png" ' \
                              'class="yui-img" title="" alt=""><br><br>4)&nbsp; But wait, inside ' \
                              "junk5.txt, there isn't anything that says it's the flag. That's because the flag has " \
                              "been encoded using an algorithm. Can you guess which encoding was used? " \
                              "Simply put the value into a decryptor and you should " \
                              "end up with the flag. <br><br>For a decryptor, you can either use " \
                              "asciitohex.com or use CrypTool which should already be installed on the desktop.<br>" \
                              '<img src="assets/img/Selection_088.png" class="yui-img" title="" alt="" ' \
                              'style="width: 379px;"><br></div>'
    email_body_footer = ' '
    email_body_footer = email_body_footer + '<br>Thank you'
    email_body_footer = email_body_footer + '<br>Your Cyber Gym Support Team<br>' \
                                            '<br>cybergym@ualr.edu</body></html>'

    email_body = str(email_body_header) + str(email_body_content) + str(email_body_footer)

    return email_body

