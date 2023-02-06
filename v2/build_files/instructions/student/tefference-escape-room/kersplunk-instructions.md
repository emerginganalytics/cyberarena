# Kersplunk Instructions
Splunk can be described as a proprietary log management tool. It is primarily used to search, monitor, analyze, and visualize machine data. With the ever growing threat of Cyber criminals, it is necessary to use tools such as Splunk to more easily keep track of what is going on within your network.
* [Basic Searching Concepts](https://lzone.de/cheat-sheet/Splunk#basic-searching-concepts)
* [Splunk’s official Splunk query syntax document](https://www.splunk.com/pdfs/solution-guides/splunk-quick-reference-guide.pdf)

## Instructions
> **_NOTE:_** Splunk typically takes around 10 minutes to start up after a fresh machine boot. The web service will not display until Splunk is fully functional.

* From within the virtual machine, click on the Firefox icon. This should automatically direct you to direct you to the local Splunk web interface at http://127.0.0.1:8000/en-US/app/launcher/home
* Once you see the log in screen, use workout and k3r$plunk8! as the username and password.
* Once logged in to the Splunk web interface, click on the **Search & Reporting** from side bar on the left. This is where the workout will take place.
> **_INFO:_** This workout is centered around an indexed dataset. In order to access this data, you will need to preface each query with the following line: index=”botsv3” earliest=0

## Basic Splunk Tips
It is best practice to refine your queries to be as exact as possible. For example, it is a lot easier for humans to parse 20 results than 150,000.
* One easy way to do this is to specify a date-time range. To the right of the Splunk search bar is a drop down menu that lets you choose over what range you want Splunk to query over.
* Surrounding a string in quotes will query data with that exact match.
* It is important to know what data you want to query over. Are you looking for an event over a specific protocol? System events?
