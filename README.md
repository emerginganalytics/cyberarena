# UA Little Rock Cyber Gym

The UA Little Rock Cyber Gym provides a hands-on cybersecurity lab environment fully built and managed in the  Google cloud. Once deployed, instructors have access to custom-built workouts in the catalog below or they can create their own workouts using yaml specifications. When ready, an instructor initiates a system build for the number of students in their class. The build takes roughly 5-10 minutes, and the instructor can then send out an individually generated link for each student. From here students have access to independently turn their workout on and off (Throughout this document, we use the term workout to refer to a cybersecurity lab).

The primary goal of the UA Little Rock cyber gym is to remove barriers that prevent students from participating in high-quality cybersecurity attack and defense simulations, and the cost is chief among these barriers. The Cyber Gym drastically reduces the cost by making workouts as close to pay-for-use as possible. Workouts are stopped as soon as they are created. Students only start cloud resources when they are ready to work, and then all resources are automatically turned down when a student is no longer working. This reduces cloud computing costs to the minimum necessary for students to perform the mission.

On the student end, we minimize requirements for personal computing and software installation. All workout interaction occurs using modern browser capabilities to emulate their connections to high-end computing resources. 

Some schools have additional hurdles because computing environments are administratively locked down to prevent software installation and nefarious outbound Internet connections. The Cyber Gym adapts to this environment by tunneling all interaction to a named server on the Internet. All traffic goes through named servers on the Internet, and named DNS services are automatically created with each new workout. Likewise, firewalls are automatically set up as we describe in the technical details section below.

Finally, the cloud resources we use are minimally scaled to provide the necessary service for completing a workout. In workouts associated with web attacks and cryptography exercises, this could mean costs as low as a fraction of a cent per hour. Whereas other workouts with a full organizational network may cost as much as 30 cents an hour.

## Setup
Before running the application setup scripts you need to perform the following tasks:
1) Create a new Google Cloud Project: https://console.cloud.google.com/
2) Install the Google Cloud SDK: https://cloud.google.com/sdk/install
3) Add this repository to your new Google Cloud Project: https://source.cloud.google.com/
4) Purchase a DNS zone or add an existing and tie it to your Google Cloud Project: https://cloud.google.com/dns/docs/quickstart

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

