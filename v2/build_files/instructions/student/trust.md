# Understanding Trust Workout Instructions
In this exercise, you will explore the dangers of misapplied trust and its impact on cybersecurity. The fundamental principle of cybersecurity revolves around establishing trust through secure engineering practices. Many cyber attacks are successful because individuals either misplace their trust or lack a solid foundation for trusting the systems they interact with.

During this exercise, you will examine trust from the perspective of an adversary and attempt to gain the trust of a target. This will be achieved through a technique known as a credential harvesting attack. These attacks involve duplicating a website's login page that the user trusts and deceiving them into entering their credentials on the fraudulent site.

> **Background:** Credential harvesting attacks are frequently associated with phishing, where deceptive emails direct users to malicious websites to collect their credentials, such as passwords, for the targeted site. For instance, an attacker might exploit social media platforms. Once they acquire the user's credentials, they can either gain unauthorized access to the social media account or exploit the fact that people often reuse passwords across multiple accounts, including banking accounts. By understanding these techniques and their implications, you will develop a deeper awareness of the importance of trust and the potential vulnerabilities that can arise when misused or exploited.

Begin your workout by clicking _Start Workout_. Then, wait a minute or two, and you can click _Connect to Server_ by the Kali server. You may need to refresh your browser after a few minutes. Once connected, this will take you to your Kali server. On the desktop right-click and select to open a command terminal. 
At the command terminal, type in ssh kali@10.1.1.30. At the password prompt, type P@55w0rd!. This will log you into your Kali Linux workstation. 
Once in Kali, you will be using the tool Social Engineering Toolkit provided as open-source by TrustedSec and authored by David Kennedy. Follow these instructions to mount the attack: 
1. To use the tool type sudo setoolkit at the command line and retype the password from above. 
2. The tool will prompt you to agree to the terms of use. If you agree, type y to continue. Then a menu will pop up with various attack modules. 
3. Select 1) Social Engineering Attacks 
4. For the type of attack to mount, select 2) Website Attack Vectors 
5. Next, select 3) Credential Harvester Attack Method. 
6. Then, you will be provided options for generating the fake website. Choose the first method, which pulls predefined web templates: 1) Web Templates 
7. The tool will take a few seconds to prepare, and then it will ask you the IP address of the attacker machine. Type in 10.1.1.30. For this workout, the fake website and the harvester are the same. This would not typically be the case. 
8. Finally, you will be provided with a template for the fake website. Use 2. Google.

To see your new credential harvester, open a browser on your workout desktop, and go to http://10.1.1.30, and type in some fake credentials. When you return to the kali command line, you should be able to see the credentials entered. 

