# Firewall KISS

In this workout, you will learn the **Keep it Simple** principle of security by managing a firewall. You will work with a real industry firewall common to many companies. Fortinet manufactures high-end, next-generation firewalls, and we offer this workout opportunity through their generosity.

To get started, follow these steps:

1. **Login**: Access your firewall through the Guacamole server. Open a browser in the Guacamole server and go to [https://10.1.1.10](https://10.1.1.10). In your browser, click "Advanced" and then scroll down to click "**Accept risk and Continue**". Use the following login credentials:
    - Username: admin
    - Password: Let’s workout!

2. **Initial Prompts**: After logging in, you'll see a prompt. Click "Login Read-Write". You might also encounter a warning about the device being managed by a FortiManager device. While normally you'd use FortiManager for changes, for this workout, you'll edit the firewall directly. Click "**Yes**" to proceed. You might receive a prompt to register the device – click "**Later**".

<img width="761" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/23300948-9f18-44ba-937f-279be0c9b4fa">

<img width="771" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/270174e1-7738-4728-9613-c758ba5347bf">


3. **Your Mission**: Your goal is to configure the firewall on the Cyber Gym server (IP address 10.1.1.2) to restrict traffic between the Demilitarized Zone (DMZ) network and the internal network.

   **Task 1**: Block DMZ to Internal Network Traffic
   - Go to "Policy & Objects IPv4 Policy" and find the firewall rules related to DMZ to Internal Network traffic.
   - Regular port scans will come from the DMZ into the inbound network. Identify the source of the scan traffic by checking the Forward Traffic Logs.
  
   - <img width="388" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/6fd86305-2457-4aef-a379-db02c86b030e">

   - Edit the rules in the IPv4 policy to block this traffic. You can delete or disable rules as needed. The goal is to prevent the port scan traffic from reaching the internal network.
  
   - <img width="502" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/740a0a32-9db1-472c-bcb6-f8755af0f1d8">

<img width="788" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/0e4d0a9e-249f-46b7-a423-a7ede7090485">


   **Task 2**: Allow Specific Traffic
   - You want to permit VNC (including port TCP/5901) and Ping traffic through the firewall from the server that's sending the port scan traffic to your internal Cyber Gym server.
   - Create a new firewall rule:
     - Name the rule.
     - Set Incoming and Outgoing interfaces to DMZ and Internal, respectively.
     - Make sure to disable Network Address Translation (NAT).

       <img width="751" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/7db8b577-10e8-4345-a520-611938a2c906">


   **Task 3**: Simplify Firewall Management
   - Apply the Keep it Simple principle to clean up rules from DMZ to Internal network:
     - Use descriptive names for rules.
     - Group rules logically.
     - Add comments with the date, your initials, and a short description for clarity.
    
       <img width="795" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/ccba56da-94e7-4a90-a731-e32c052f2116">
       <img width="792" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/e8b48f83-cd9e-4bbf-a82d-6bd154b1cebb">
       <img width="789" alt="image" src="https://github.com/emerginganalytics/cyberarena/assets/71454038/59d5714a-6616-4738-b498-9119ead4ce05">

Comment on rules by scrolling down and using the provided field.

   - Take a screenshot of the final rule configuration and upload it for assessment.

This exercise aims to help you understand the basics of firewall management while applying security principles. Have fun learning!
