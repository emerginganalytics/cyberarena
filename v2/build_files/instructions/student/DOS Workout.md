# Denial of Service (DoS) Workout Instructions

Welcome to your team's Denial of Service workout. In this activity, you'll learn about the impact of a denial of service attack on a computer system. A Denial of Service (DoS) attack happens when someone tries to block access to a computer, device, or network. This is usually done by flooding the target computer with a huge amount of network data. This flood of data can slow down the computer's response or even make it completely unavailable. In this workout, you'll simulate a DoS attack on a web server and see how it affects the computer's performance.

## Your Goal
There are two parts to this activity. In the first part, you need to make sure the computer's CPU usage stays above 40%. In the next part, you'll do some additional setup and aim to keep the CPU usage above 70%.

## Getting Started
1. Open a special type of window on the computer called a terminal.
2. In the terminal, type: `ssh cybergym@10.1.1.33`
3. If you see a warning about the connection, it's okay to proceed. Enter the password: `Let’s workout!`

## Monitoring CPU Usage
1. Type the following command in the terminal: `sar -u 1 1000`
2. This will show you the CPU usage every second for 1000 seconds.

## Starting the Attack
1. Open a new tab in the terminal.
2. In this new tab, type: `cd LOIC`
3. Run the following command: `./loic-net4.5.sh run`
4. This starts a tool for simulating the attack. Remember, this should only be used for learning here and not on other computers outside this controlled environment.

## Setting Up the Attack
1. In the tool, enter the target IP address as `10.1.1.33` and click "Lock On."
2. Change the attack method to HTTP and click the "ready" button to start flooding the web server with data.

## Observing the Effects
1. Go back to the first terminal and watch how the CPU usage changes.
2. Keep the attack going for 3 to 5 minutes.
3. An assessment will mark your workout as complete when you're done.

## Stopping the Attack
1. Stop the attack in the tool.
2. Watch as the CPU usage goes back to normal.

## Protecting the Server
1. If you completed the assessment, try protecting the server from this attack.
2. Stop the CPU usage command by pressing `Ctrl-c` in the terminal.
3. Type: `sudo ufw deny html from 10.1.1.9`
4. Run the CPU usage command again to see the CPU usage.

## Re-Running the Attack
1. Start the attack tool again without changing any settings.
2. Notice any feedback about failed packets from the attack tool.
3. Watch the CPU usage on the web server's terminal.

Remember, the purpose of this exercise is to learn about these concepts in a safe environment. Using these techniques on other computers without permission is considered a cyber attack and is against the law.
