# Rebel Base Access Control Mission
This code implements a graphical user interface (GUI) application for managing access control in the Rebel Base 
server infrastructure. It allows system administrators to perform various assessment tasks based on their
experience level, such as removing old user accounts, evaluating group memberships, and applying role-based 
access control policies.

## Installation and Requirements
The code requires Python and the following modules: win32net and tkinter.

Use pyinstaller to deploy the application to the `dist` directory. In the future, will create a setup script
to synchronize the distribution directory. Pyinstaller does not seem to synchronize the data folder. In the
meantime, run:
```
pyinstaller .\rebel_base_startup.spec
```

## Usage
This should be run on the `cyberarena-keepitsimple-ac` server, which has the users, groups, and folders
set up for the lab. Copy the dist folder into the target server at `C:\.assessment`. A shortcut to the 
executable is in the startup folder on the target server.

When the user logs in, a window titled "Rebel Base Access Control Mission" will appear.
Click the "Your Mission" button to view the mission instructions.
Choose the appropriate assessment level (Youngling, Padawan, or Jedi Master) by clicking the respective button.

Upon successful completion, a certificate will be displayed. The certificates are encrypted in a zip archive 
until the successful completion of the assignment. Users can complete multiple exercises.

## License
This code is provided under the MIT License.

Feel free to modify and use the code to enhance access control management in your own systems.

## Acknowledgments
This code was developed as part of a cybersecurity course at UA Little Rock to teach students about the keep
it simple principle in cybersecurity operations.

If you have any questions or need further assistance, please feel free to contact Philip Huff at 
phuff@ualr.edu.

May the Force be with you as you embark on this important access control mission!
