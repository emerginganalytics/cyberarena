# Denial of Service Instructions
Welcome to your team's Denial of Service workout where you will learn about the
loss of availability effects of a denial of service attack. A Denial of Service (DoS)
attack occurs when an adversary prevents access to a system, device, or network
resource, and this often occurs through a flood of network traffic directed at a
target computer. That network traffic can be thousands of data packets per second
directed at a network service. It can cause a delay in response to the user or
prevent them from accessing the service altogether. In this workout, you will
conduct a DoS attack on a webserver and witness its effect on CPU usage.

> **_WARNING:_**  The tools used in this workout should only be used for learning
purposes in this controlled environment. Using these tools on other
computers outside of the Cyber Arena is considered a cyber attack and may
result in criminal penalties.

Follow the instructions to target a web server and maintain a 70% utilization of the target CPU.
Your workout will be assessed once a minute to ensure you maintain over 70% CPU utilization.

## Instructions
* A terminal should be up when you initially login. Type in ssh cybergym@10.1.1.33. Accept the 
ssh key warning and then 
* type in the password `Let’s workout!`
* Type in the following command to output CPU usage every second for a 1000 seconds and view 
the current CPU usage: `sar -u 1 10000`
* Open a new tab in the terminal by clicking File New Tab. In the new tab, change your 
directory to LOIC/, `cd LOIC`
* Run the following shell script by typing in `./loic-net4.5.sh run`
* In the Low Orbital Ion Cannon Tool, target the webserver at the IP address
10.1.1.33 by typing it in the Select Your Target IP field. Then click Lock On.
* You will need to identify how to target the server using LOIC that will ensure
the computer goes beyond 70% CPU utilization.
