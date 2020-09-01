# [ Arena Build Password Attack ]
---   
This workout is used primarily by the CyberGym Arena builds. Currently, the flag is statically created, but future    
implementations will provide dynamic flag creation.  

**7/13/2020**   

- Updated program to allow for dynamic PIN creation. Flag remains static.   
- Fixed issue where 0 could not be the first entered value and where multiple zeroes could not be entered in a row
   
   
### [ NOTE ]:   
In order to modify this workout, developers will need to install and set up QT. QT is a free and   
open-source platform used to build GUI's by extending the C++ language.   

### Building a standalone application   
After you have compiled the source using either command line *qmake* and *nmake* tools or the built in compiler in QT Creator,   
you need to make sure the all the correct dependencies are in the directory that holds your executable.   

- Open up the MSVC terminal and navigate to the release folder of your executable.   
- Once there, run the following command: ```windeployqt.exe --quick . ```   

This will place get all the dependencies needed for the program to run to successfully run on another machine. Compress the   
current folder and drop it on the target machine.
