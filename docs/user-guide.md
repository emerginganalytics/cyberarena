# UA Little Rock Cyber Gym User Guide

Introduction
============

This material is based upon work supported by the National Science Foundation under Grant No. 1623628

The UA Little Rock Cyber Gym provides a hands-on cybersecurity lab environment fully built and managed in the  Google cloud. Once deployed, instructors have access to custom-built workouts in the catalog below or they can create their own workouts using yaml specifications. When ready, an instructor initiates a system build for the number of students in their class. The build takes roughly 5-10 minutes, and the instructor can then send out an individually generated link for each student. From here students have access to independently turn their workout on and off (Throughout this document, we use the term workout to refer to a cybersecurity lab).

The primary goal of the UA Little Rock cyber gym is to remove barriers that prevent students from participating in high-quality cybersecurity attack and defense simulations, and the cost is chief among these barriers. The Cyber Gym drastically reduces the cost by making workouts as close to pay-for-use as possible. Workouts are stopped as soon as they are created. Students only start cloud resources when they are ready to work, and then all resources are automatically turned down when a student is no longer working. This reduces cloud computing costs to the minimum necessary for students to perform the mission.

On the student end, we minimize requirements for personal computing and software installation. All workout interaction occurs using modern browser capabilities to emulate their connections to high-end computing resources. 

Some schools have additional hurdles because computing environments are administratively locked down to prevent software installation and nefarious outbound Internet connections. The Cyber Gym adapts to this environment by tunneling all interaction to a named server on the Internet. All traffic goes through named servers on the Internet, and named DNS services are automatically created with each new workout. Likewise, firewalls are automatically set up as we describe in the technical details section below.

Finally, the cloud resources we use are minimally scaled to provide the necessary service for completing a workout. In workouts associated with web attacks and cryptography exercises, this could mean costs as low as a fraction of a cent per hour. Whereas other workouts with a full organizational network may cost as much as 30 cents an hour.

Setup
=====
Before running the application setup scripts you need to perform the following tasks:
1) Create a new Google Cloud Project: https://console.cloud.google.com/
2) Install the Google Cloud SDK: https://cloud.google.com/sdk/install
3) Add this GitHub repository to your new Google Cloud Project: https://source.cloud.google.com/
4) Purchase a DNS zone or add an existing and tie it to your Google Cloud Project: https://cloud.google.com/dns/docs/quickstart. Here you'll enable the Cloud domains API at https://console.cloud.google.com/net-services/domains. Then click to register the domain. Use the recommended Cloud DNS, but for the Cloud DNS Zone, select to setup a new zone, and change the name to cybergym-public.
5) Set up the identity service for application authentication using the [Authentication Setup Guide](https://github.com/emerginganalytics/ualr-cyber-gym/blob/master/docs/auth_setup.md)

Run the build script in the cloud-build-scripts folder. This will walk through all of the steps to set up your applications and cloud functions to run on your project. There is no cost at this point except negligible costs for storage and cloud function run time. Costs will begin accumulating once students run their first workout.

Once everything is set up, you will need to increase the default cloud quotas. Increase quotas according the following recommendations based on Max Concurrent Build (MCB):
 1) Compute Engine API (Subnetworks) - MCB * 2
 2) Compute Engine API (Networks) - MCB * 1
 3) Compute Engine API (Firewall Rules) - MCB * 3
 4) Compute Engine API (Routes) - MCB * 2
 5) Compute Engine API (In-Use IP Addresses) - MCB * 1
 6) Compute Engine API (CPUs) - MCB * 3
 7) Cloud Build API (Concurrent Builds) - 50

You may need to contact a cloud sales representative to permit these quotas.

Technical Details
=================

This section provides a technical overview of the Cyber Gym.

Individual Workout Mode
-----------------------
For several workouts, students are performing a specific task in which network interaction with the class is not required. This is also the case for more basic workouts in which students will likely not have the skills to perform interactive workouts on the same network. Instead, the instructor builds individual networks for each student or team, and then each student or team will perform the mission independently. The instructor may wish for students to still compete against the clock, and the automatic assessment will support this competition.

Arena Mode
----------
Arena mode workouts have all students in the same network, and they either compete in a red-team/blue-team exercise or they can work together to fulfill a common mission.

Workout Specification
---------------------

Yaml files are used in the UA Little Rock Cyber Gym to specify automatic cloud builds of _workouts_ for students. By using yaml files, one only needs to create the server images you want to replicate and then describe the build according to this specification. Then you can build the same _workout_ for students millions of times.

The files are uploaded to a Google Cloud bucket, in which the web application looks. This way, workout builders do not need to change the application. They only need to specify the YAML. We are currently beta testing an interface to build the YAML specifications. The following sections describe the YAML specification.

### Workout Section
Specify attributes about your workout in the _workout_ section of the YAML file. Use the following fields to describe your workout:
*   **name** (required): The name of your workout, which will be shown to the instructors and students.
*   **workout\_description** (required): A high-level description of your workout. This should only be a sentence or two. For detailed descriptions, use the instructions URL, described below.
*   **student\_instructions\_url**: The URL of the document containing the student instructions for the workout. This might be in Google Docs or Confluence.
*   **instructor\_instructions\_url**: The URL of the document containing the instructor instructions for the workout. This might be in Google Docs or Confluence

### Network Section

In this section, the network build is specified. More than one network can be built for a workout, and servers are placed into the named networks as specified in the _servers_ section. The names must be unique. Currently, it is not possible to route between subnetworks in the Google Cloud VPC. So, if you would like to include a routing device (i.e. a firewall) in the workout, then you'll need to create multiple networks instead of multiple subnetworks. Specify the list of networks using the dash character:

*   **name** (required): the unique name of the network
*   **subnets** (required): Every network must have at least one subnet.
    *   **name** (required): You can simply name this default if there is only one. If there is more than one, then the name of the subnet must be unique.
    *   **ip\_subnet** (required): The IP subnet in CIDR format (e.g. 10.1.1.0/24).
        

### Student Entry
The Cyber Gym will build a guacmole proxy according to these specifications. In this section, you point the proxy to the server where the student should have an interactive desktop. Credentials to the server are provided for the proxy connection. These settings specify the parameters for configuring the guacamole proxy connection.

*   **type** (required): Either RDP for a Windows desktop or VNC for a Linux desktop
*   **domain** (For Windows RDP connections having an Active Directory Domain Controller): The domain name prefix used for login.
*   **username** (For Windows RDP connections only): The username used for connecting to the RDP session
*   **password** (required): Either the Windows RDP password or the VNC password for the Linux desktop
*   **network** (required): The network in which the desktop resides
*   **ip** (required): The IP address of the server that students will land on
    
### Servers Section
The servers section specifies which images you want to be brought up and in which network. The first server we have is known as _labentry_, which should run an Apache Guacamole instance for students to hop to other servers. This can be copied into the YAML as follows:

*   **name**: cybergym-cyberattack
*   **image**: image-cyberattack (or a similarly named image in the cloud project)
*   **tags**: {items: \["http-server", "labentry"\]
*   **nics**:
    *   **network**: (Named network from _networks_ section)
    *   **internal\_IP**: (Something within the designated subnet)
    *   **subnet**: (Named subnet from the _networks_ section)
    *   **external\_NAT**: Defaults to False (This ensures it is externally accessible)
        

The server fields are further described as follows:

*   **name** (required): What you wish to name the server
*   **build_type** (optional): Specify "machine-image" to support the GCP beta machine image build
*   **image** (required): This image name must already exist in the cloud project
*   **machine\_type** (optional): By default, this is "n1-standard-1", which works for most Windows and Linux desktops.
*   **machine\_image** (optional): When specifying the build\_type, use this to specify the machine image to build
*   **network\_routing** (optional): Boolean on whether this is a network router. By default, this is False and only needs to be specified when you have a router in the network.
*   **tags** (optional): A dictionary list of tags to assign the server, which is used for the firewall.
*   **metadata** (optional): By default this is None, but it may include metadata such as startup scripts.
*   **sshkey** (optional): Add the public ssh key if, for instance, you have a Linux server in which you want the user to authenticate through ssh using a custom user. An example ssh public key string for the user gymboss is: "gymboss:ssh-rsa AAAAB3N..== gymboss"
*   **include_env** (optional): Specify true to indicate the project and workout environment variables should be included on this server. These get added through a startup script and include the project's URL and the workout ID.
*   **operating-system** (optional): windows or linux. Right now this is used for loading environment variables onto the server at build.
*   **nics** (required): This specifies the network connections for the servers. Unless this is a firewall/router, then only one nic is needed. The fields are the same as those specified in the guacamole description above.
    

### Routing Section (Optional)

Use this section if you have a firewall/router in the workout. This will ensure routes flow through the device. The firewall/router must be specified in the section above with NICs into all of the networks specified in the routing section. Note, a firewall/router with an external, internal, and DMZ network would have 4 routes: (1) default internal, (2) default DMZ, (3) external to internal, and (4) external to DMZ.

*   **name** (required): Unique route name.
    
*   **network** (required): The network name of the route. This must be from the above network section.
    
*   **dest\_range** (required): For _internal_ networks, this would most likely be "0.0.0.0/0". However, if you have an _externally_ facing network, then you will need a route path for each of the subnets.
    
*   **next\_hop\_instance** (required): The firewall/router device specified in the servers section.
    

### Firewall Section

This section specifies the firewall rules to open for the workout. You should include a firewall rule to allow external access to the Apache Guacamole server, and you should include rules to allow connections between different networks if you are including a firewall/router. This is a list of rules under **firewall\_rules**.

*   **name** (required): Specify what is allowed (e.g. allow-http). This is just the name and must be unique for the workout.
    
*   **network** (required): Specify the named network where this rule applies (from the networks list above)
    
*   **target\_tags**: A list of target tags this applies to. Tag servers in the relevant section above and then use this to only apply to given servers (e.g. \["http-server"\])
    
*   **protocol** (required): Specify none if using multiple protocols, but for TCP only, specify tcp, etc.
    
*   **ports** (required): A list of ports in the format \["PROTOCOL/PORT NUMBER"\]. The port numbers can be comma-separated. A few examples include \["tcp/80,8080,443"\] or \["tcp/any", "udp/any", "icmp/any"\]
    
*   **source\_ranges** (required): Limit the source IP addresses to which this rule applies. If this is an external rule, use _any_, i.e. \["0.0.0.0/0"\].
    

### Assessments

See documentation for Cyber Gym Assessments: [Cyber Gym Assessments](https://eac-ualr.atlassian.net/wiki/spaces/C/pages/141066257/Cyber+Gym+Assessments)

Arena Specification
-------------------

A significant component of the build is a guacamole connection provided for each student by default. The guacamole server resides in the student-network and has connections to all student entry servers with a username and password generated at build time. The username and password reside in the data store under each of the workouts.

### Workout/Arena Section

Specify attributes about your workout in the _workout_ (or arena when we fix this) section of the YAML file. Use the following fields to describe your workout:

*   **name** (required): The name of your workout, which will be shown to the instructors and students.
*   **build type** (required): Specify arena
*   **workout\_description** (required): A high-level description of your workout. This should only be a sentence or two. For detailed descriptions, use the instructions URL, described below.
*   **student\_instructions\_url**: The URL of the document containing the student instructions for the workout. This might be in Google Docs or Confluence.
*   **instructor\_instructions\_url**: The URL of the document containing the instructor instructions for the workout. This might be in Google Docs or Confluence.

### Student Servers Section

This section specifies the build for each student in the arena. This is copied into the build specification for as many students are specified in the build.

*   **student\_entry** (required): The name of the server in this section to use for entry into the arena for each student
*   **student\_entry\_type** (required): rdp or vnc. This is the protocol to use for connecting to the student entry server
*   **student\_entry\_username** (required): The username for connecting to student entry
*   **student\_entry\_password** (required): The password for connecting to student entry
*   **network\_type** (required): same or distinct. This will most likely be the same, but there is an option to have distinct networks in the arena for each student. A distinct network build is still in development
*   **servers** (required): An array of servers you want built for each student.
    *   **name:** name suffix of the server. One of these should match the student\_entry from above
    *   **image:** The image to use for building the server
    *   **machine\_type:** The type of cloud machine to use in the build
    *   **internal\_ip:** This can only be used for a network type of ‘same’ right now. You must specify a server IP in the range 10.1.0.101-254.

### Additional Network Section (optional)

In this section, you can add any additional-network. The default network is student-network which contains all of the student entry servers.

*   **name** (required): the unique name of the network
*   **subnets** (optional): Every network must have at least one subnet.
    *   **name** (optional): You can simply name this default if there is only one. If there is more than one, then the name of the subnet must be unique.
    *   **ip\_subnet** (optional): The IP subnet in CIDR format (e.g. 10.1.1.0/24).

### Additional Servers Section

The servers section specifies which images you want to be brought up and in which network. The first server we have is known as _labentry_, which should run an Apache Guacamole instance for students to hop to other servers. This can be copied into the YAML as follows:

*   **name**: cybergym-labentry
*   **image**: image-labentry (or a similarly named image in the cloud project)
*   **nics**:
    *   **network**: (Named network from _networks_ section)
    *   **internal\_IP**: (Something within the designated subnet)
    *   **subnet**: (Named subnet from the _networks_ section)
    *   **external\_NAT**: true (This ensures it is externally accessible)
        

The server fields are further described as follows:

*   **name** (required): What you wish to name the server.
*   **image** (required): This image name must already exist in the cloud project
*   **machine\_type** (optional): By default, this is "n1-standard-1", which works for most Windows and Linux desktops.
*   **network\_routing** (optional): Boolean on whether this is a network router. By default, this is False and only needs to be specified when you have a router in the network.
*   **tags** (optional): A dictionary list of tags to assign the server, which is used for the firewall.
*   **sshkey** (required): Add the public ssh key if, for instance, you have a Linux server in which you want the user to authenticate through ssh using a custom user. An example ssh public key string for the user gymboss is: "gymboss:ssh-rsa AAAAB3N..== gymboss"
*   **nics** (required): This specifies the network connections for the servers. Unless this is a firewall/router, then only one nic is needed. The fields are the same as those specified in the guacamole description above.
    
### Routing Section (Optional)

See the workout section for a full specification of routing

### Firewall Section

See the firewall section for a full specification of firewall rules

### Assessments

Assessments are a work in progress for arenas. See documentation for Cyber Gym Assessments: [Cyber Gym Assessments](https://eac-ualr.atlassian.net/wiki/spaces/C/pages/141066257/Cyber+Gym+Assessments)

Cloud Functions
-------------------

The following cloud functions must be installed along with the topics and scheduler. These functions are containers for managing the lifecycle of any given workout.

<table data-layout="default"><colgroup><col style="width: 154.0px;"><col style="width: 259.0px;"><col style="width: 346.0px;"></colgroup>

<tbody>

<tr>

<th>

**Function**

</th>

<th>

**Description**

</th>

<th>

**Schedule**

</th>

</tr>

<tr>

<td>

function-build-workouts

</td>

<td>

Builds a single workout according to a specification and sets the correct datastore flag when complete.

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _build-workouts_

</td>

</tr>

<tr>

<td>

function-start-workout

</td>

<td>

Starts all workout resources. This is to offload long-running tasks from the web application.

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _start-workout_

</td>

</tr>

<tr>

<td>

function-stop-start-workout

</td>

<td>

Stops and starts all workout resources. This is to offload long-running tasks from the web application

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _stop-start-workout_

</td>

</tr>

<tr>

<td>

function-delete-expired-workouts

</td>

<td>

Deletes any workout resources (i.e., servers, networks, routes, firewall rules, DNS entries) past its expiration date listed in the datastore.

</td>

<td>

Runs **hourly** through _maint-del-job_ cloud scheduler. Triggers pub/sub topic: _maint-del-systems_

</td>

</tr>

<tr>

<td>

function_stop_workouts

</td>

<td>

Stops any workouts which are running beyond their specified runtime as listed in the datastore.

</td>

<td>

Runs **every 15 minutes** through _stop-workouts_ cloud scheduler. Triggers pub/sub topic: _stop-workouts_

</td>

</tr>

<tr>

<td>

function_wrong_state_checker

</td>

<td>

There are circumstances in which a server may be running when their datastore state is listed as _stopped_. This function will correct the state

</td>

<td>

Runs **daily** through _wrong_state_checker_ cloud scheduler. Triggers pub/sub topic: _wrong_state_checker_

</td>

</tr>

<tr>

<td>

function-build-arena

</td>

<td>

Build an arena of multiple student servers and multiple central servers

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _build-arena_ with unit_id passed in the context

</td>

</tr>

<tr>

<td>

function-stop-arenas

</td>

<td>

Stops any arenas running beyond their specified run time

</td>

<td>

Runs **every 15 minutes** through _job-stop-lapsed-arenas_ cloud scheduler. Triggers pub/sub topic: _stop-lapsed-arenas_

</td>

</tr>

<tr>

<td>

function-delete-expired-workouts

</td>

<td>

Delete any expired or misfit arena resources

</td>

<td>

Runs **hourly** through _job-delete-expired-arena_ cloud scheduler. Triggers pub/sub topic: _delete-arena_

</td>

</tr>

<tr>

<td>

function-stop-all-workouts

</td>

<td>

Stops all running workouts

</td>

<td>

Runs **daily** at midnight through _job-stop-all-servers_ cloud scheduler. Triggers pub/sub topic: _stop-all-servers_

</td>

</tr>

<tr>

<td>

function-start-arena

</td>

<td>

Starts arena servers

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _start-arena_ with unit_id passed in the context

</td>

</tr>

</tbody>

</table>
