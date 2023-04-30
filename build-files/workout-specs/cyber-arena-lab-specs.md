# Cyber Arena Lab Specifications
Specifications are encrypted in the repository. To view or modify them follow the instructions here:
[Encrypting/Decrypting](docs/build-locker.md). Decrypting the files will place them in a local folder called 
_needs-encrypted_ in this directory. You can then encrypt the files when you have finished modifying them.

## Cyber Arena Learning Experiences
1. **Workout**: Instructors can create and assign labs to groups of students using a join code. Students only need this code, and their email address identifies them for future access. Workouts are designed within a unit specification, providing each student with a unique learning environment.
2. **LMS Assignment**: Similar to workouts, LMS assignments integrate assessment questions with a Learning Management System (LMS). Instructors deploy labs by selecting a course, which generates workouts for each student. Students access labs using a join code and their LMS-associated email address. Additionally, a quiz is automatically created and assigned to each student. Labs are built when students first access them, allowing for asynchronous learning within a set time frame.
3. **Escape Room**: A unique setup featuring multiple, independent team labs that include all resources needed for an escape room experience. These cloud-based components are woven into a narrative storyline. Instructors create the resources and initiate the escape room when teams are ready to participate.
4. **Classroom**: Designed for engaging all students in a shared lab environment. Instructors can specify additional student servers to include within the central set of shared resources. Classrooms are built in a fixed arena, where multiple classrooms can be configured, but only one can exist at a time. However, several fixed arenas can coexist within a cloud project.

## Authoring and Publishing New Labs
Yaml files are used in the UA Little Rock Cyber Gym to specify automatic cloud builds of _workouts_ for students. 
By using yaml files, one only needs to create the server images you want to replicate and then describe the build 
according to this specification. Then you can build the same _workout_ for students millions of times.

The files are uploaded to the Google Cloud bucket <project-name>_cloudbuild/yaml-build-files/, in which the web application looks. This way, workout builders do not 
need to change the application. They only need to specify the YAML. We are currently beta testing an interface to build
 the YAML specifications. The following sections describe the YAML specification.
 
## Schema
Specifications are serialized according to a schema (include location...)

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
