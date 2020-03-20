# Building Your YAML File
Yaml files are used in the UA Little Rock Cyber Gym to specify automatic cloud builds of _workouts_ for students. By using yaml files, one only needs create the server images you want to replicate and then describe the build according to this specification. Then you can build the same _workout_ for students millions of times.

The files are uploaded to a Google Cloud bucket, in which the web application looks. This way, workout builders do not need to change the application. They only need to specify the yaml.

Prerequisites for documenting the yaml file include:
* Configuring your server images
* Configuring and testing your Apache Guacamole connection through VNC or RDP
## Workout Section
Specify attributes about your workout in the _workout_ section of the yaml file. Use the following fields to describe your workout:
* **name** (required): The name of your workout, which will be shown to the instructors and students.
* **workout_description** (required): A high level description of your workout. This should only be a sentence or two. For detailed descriptions, use the instructions URL, described below.
* **student_instructions_url**: The URL of the document containing the student instructions for the workout. This might be in Google Docs or Confluence.
* **instructor_instructions_url**: The URL of the document containing the instructor instructions for the workout. This might be in Google Docs or Confluence.
* **project_name** (optional): This is the name of the cloud project in which you are building. The default will be specified in the application.
* **region** (optional): Default is "us-central1"
* **zone** (optional): Default is "us-central1-a"
* **dnszone** (optional): Default will be specified in the application. This is the named zone in which you can programatically manage the DNS mappings to the ephemereal public IP addresses in the workout.

## Network Section
In this section, the network build is specified. More than one network can be built for a workout, and servers are place into the named networks as specified in the _servers_ section. The names must be unique. Currently, it is not possible to route between subnetworks in the Google Cloud VPC. So, if you would like to include a routing device (i.e. a firewall) in the workout, then you'll need to create multiple networks instead of multiple subnetworks. Specify the list of networks using the dash character:
* **name** (required): the unique name of the network
* **subnets** (required): Every network must have at least one subnet.
    * **name** (required): You can simply name this default if there is only one. If there is more than one, then the name of the subnet must be unique.
    * **ip_subnet** (required): The IP subnet in CIDR format (e.g. 10.1.1.0/24).
    
## Servers Section
The servers section specifies which images you want brought up and in which network. The first server we have is known as _labentry_, which should run an Apache Guacamole instance for students to hop to other servers. This can be copied into the yaml as follows:
  * **name**: cybergym-labentry
  * **image**: image-labentry (or a similarly named image in the cloud project)
  * **tags**: {items: ["http-server", "labentry"]}
  * **nics**:
      - **network**: (Named network from _networks_ section)
      - **internal_IP**: (Something within the designated subnet)
      - **subnet**: (Named subnet from the the _networks_ section)
      - **external_NAT**: true (This ensures it is externally accessible)
      
The server fields are further described as follows:
  * **name** (required): What you wish to name the server.
  * **image** (required): This image name must already exist in the cloud project
  * **machine_type** (optional): By default this is "n1-standard-1", which works for most Windows and Linux desktops.
  * **network_routing** (optional): Boolean on whether this is a network router. By default, this is False and only needs to be specified when you have a router in the network.
  * **tags** (optional): A dictionary list of tags to assign the server, which is used for the firewall.
  * **metadata** (optional): By default this is None, but it may include meta data such as startup scripts.
  * **sshkey** (required): Add the public ssh key if, for instance, you have a Linux server in which you want the user to authenticate through ssh using a custom user. An example ssh public key string for the user gymboss is: "gymboss:ssh-rsa AAAAB3N..== gymboss" 
  * **guac_path** (optional): The Apache Guacamole server assigns a default string to a given network configuration. This is usually copied over when testing and assigned here. An example string might look like: "MjQAYwBteXNxbA==". Using this string, the student can access the interactive server through an Apache Guacamole URL.
  * **nics** (required): This specifies the network connections for the servers. Unless this is a firewall/router, then only one nic is needed. The fields are the same as those specified in the guacamole description above.

## Routing Section (Optional)
Use this section if you have a firewall/router in the workout. This will ensure routes flow through the device. The firewall/router must be specified in the section above with NICs into all of the networks specified in the routing section. Note, a firewall/router with an external, internal and DMZ network would have have 4 routes: (1) default internal, (2) default dmz, (3) external to internal and (4) external to dmz.
* **name** (required): Unique route name.
* **network** (required): The network name of the route. This must be from the above network section.
* **dest_range** (required): For _internal_ networks, this would most likely be "0.0.0.0/0". However, if you have an _externally_ facing network, then you will need a route path for each of the subnets.
* **next_hop_instance** (required): The firewall/router device specified in the servers section.

## Firewall Section
This section specifies the firewall rules to open for the workout. You should include a firewall rule to allow external access to the Apache Guacamole server, and you should include rules to allow connections between different networks if you are including a firewall/router. This is a list of rules under **firewall_rules**. 
* **name** (required): Specify what is allowed (e.g. allow-http). This is just the name and must be unique for the workout.
* **network** (required): Specify the named network where this rule applies (from the networks list above)
* **target_tags**: A list of target tags this applies to. Tag servers in the relevant section above and then use this to only apply to given servers (e.g. ["http-server"])
* **protocol** (required): Specify none if using multiple protocols, but for TCP only, specify tcp, etc.
* **ports** (required): A list of ports in the format ["PROTOCOL/PORT NUMBER"]. The port numbers can be comma separated.  A few examples include ["tcp/80,8080,443"] or ["tcp/any", "udp/any", "icmp/any"]
* **source_ranges** (required): Limit the source IP addresses to which this rule applies. If this is an external rule, use _any_, i.e. ["0.0.0.0/0"].

    