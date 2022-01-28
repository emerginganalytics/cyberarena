Introduction
============

This material is based upon work supported by the National Science Foundation under Grant No. 1623628

The UA Little Rock Cyber Gym provides a hands-on cybersecurity lab environment fully built and managed in the 
Google cloud. Once deployed, instructors have access to custom-built workouts in the catalog below or they can create 
their own workouts using yaml specifications. When ready, an instructor initiates a system build for the number of
 students in their class. The build takes roughly 5-10 minutes, and the instructor can then send out an individually 
 generated link for each student. From here students have access to independently turn their workout on and off 
 (Throughout this document, we use the term workout to refer to a cybersecurity lab).

The primary goal of the UA Little Rock cyber gym is to remove barriers that prevent students from participating in 
high-quality cybersecurity attack and defense simulations, and the cost is chief among these barriers. The Cyber Gym 
drastically reduces the cost by making workouts as close to pay-for-use as possible. Workouts are stopped as soon as 
they are created. Students only start cloud resources when they are ready to work, and then all resources are 
automatically turned down when a student is no longer working. This reduces cloud computing costs to the minimum 
necessary for students to perform the mission.

On the student end, we minimize requirements for personal computing and software installation. All workout interaction 
occurs using modern browser capabilities to emulate their connections to high-end computing resources. 

Some schools have additional hurdles because computing environments are administratively locked down to prevent 
software installation and nefarious outbound Internet connections. The Cyber Gym adapts to this environment by 
tunneling all interaction to a named server on the Internet. All traffic goes through named servers on the Internet, 
and named DNS services are automatically created with each new workout. Likewise, firewalls are automatically set up as 
we describe in the technical details section below.

Finally, the cloud resources we use are minimally scaled to provide the necessary service for completing a workout. 
In workouts associated with web attacks and cryptography exercises, this could mean costs as low as a fraction of a 
cent per hour. Whereas other workouts with a full organizational network may cost as much as 30 cents an hour.

Helpful Guides
============
* [Setup](build-files/README.md) - Everything needed to setup a new instance of the Cyber Arena
* [Admin Guide](docs/admin-guide.md) - Technical guide for people administering the Cyber Arena
* [Instructor Guide](docs/instructor-guide.md) - Assists teachers in setting up workouts for their classes
* [Student Desk Reference](docs/student-guide.md) - A quick reference sheet for students
* [Workout Specifications](build-files/workout-specs/README.md) - Provides details of how to specify cloud builds as 
workouts in the Cyber Arena.
* [Cloud Functions](cloud-functions/README.md) - Cloud functions support building and maintaining workouts in the 
Cyber Arena.

## Authors
* Andrew Bomberger
* Benjamin Miller
* Carter Williams
* Chance Melby
* Mark Barnes
* Nick Stewart
* Philip Huff
* Ryan Ronquillo
* Sam Willis
* Samuel Thomas
* Verdin-Pol Gaétan
* Zachary Long

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details

## Acknowledgments
This material is based upon work supported by the National Science Foundation under Grant No. 1623628. 

Additional organizations who have been a huge help in getting cutting edge Cybersecurity labs to students:
* Google Cloud Team, particularly Marcus Forbes, Kyle Azua, and Greg Molnar in their guidance and assistance
* Fortinet for help in deploying their cloud firewall VM
* Nessus scanning engine
* Shodan for their API search engine
* National FBI Training Academy for help in finding good test images
* Forge Institute for providing guidance in the design and feature expansion