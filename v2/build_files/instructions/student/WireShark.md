# Wireshark Objectives:

The Internet enables global data transmission, but data passing through various countries and organizations can become vulnerable. Encryption, like a special lockbox, safeguards data. However, some Internet data transfer methods lack encryption, allowing malicious actors to access information.

In this exercise, we explore how malicious individuals can exploit unprotected network protocols using specialized tools to gather critical system information.

## Your Mission:

Welcome to the Recon with Wireshark workout, where you'll learn network packet analysis and understand the insecurity of numerous network protocols. In this exercise, you'll perform network traffic analysis in a simulated attack environment. By utilizing Wireshark, you'll analyze packets originating from the UA Little Rock Classified Web Application to capture credentials and log in.

There's been buzz about a secret classified server within the UA Little Rock Cyber Arena. Rumor has it that this server houses security files and vital documents. We obtained an image of a note from the new receptionist's computer.

The classified server's URL is http://10.1.1.33:5000. Let's investigate. Open Firefox and navigate to the provided IP address.

If you've reached the correct address, go ahead and click the green login button.

It seems we need the admin's password. Our analysts noticed suspicious activity when you accessed the classified server. Let's try to capture information and see what's happening. Close your browser and open the Wireshark application (blue shark fin icon) from the bottom of the screen.

Using Wireshark, we can capture packets between you and the classified server. However, we need to set a capture filter. In the capture filter field, type: `host 10.1.1.33` and press enter.

This filter lets us capture packets interacting with your computer. The password is stored in one of these captured packets. Analyze the packets to find the password. Once found, log in to the classified server and report your findings.

Best of luck!
