# Powershell Lab

## Table of Contents

## Introduction

In this lab, you will learn how to use Powershell to perform basic system administration tasks.

## Lab Instructions

### Part 1 - Powershell Basics

1. Open powershell as administrator
   1. Right click on the powershell icon in the taskbar
   2. Select `Run as administrator`
   3. Powershell will open with local administrator permissions.
2. The Powershell terminal will open with a prompt that looks like this:
   1. `PS C:\Windows\System32>`
   2. The `PS` stands for Powershell
   3. The `C:\Windows\System32` is the current directory
   4. The `>` is the prompt
3. Run the command `Get-Command` to see a list of all the commands available in powershell.
4. You will see a lot of available commands
5. To shorten the list, run the command `Get-Command | more` to see the commands one page at a time.
   1. The `|` character is called a pipe. It takes the output of the command on the left and sends it to the command on the right.
6. Next, run the command `Get-Command | Select-Object -First 10` to see the first 10 commands.
   1. The `Select-Object` command selects a subset of the objects passed to it.
   2. The `-First 10` option tells the `Select-Object` command to select the first 10 objects.
7. Next, run the command `Get-Command | Select-Object -Last 10` to see the last 10 commands.
   1. The `-Last 10` option tells the `Select-Object` command to select the last 10 objects.
8. Next let's find out how we can get help on a command.
   1. Run the command `Get-Help Get-Command` to get help on the `Get-Command` command.
   2. Get-Help will display the help for the command in the powershell window.
   3. You can also get help on a command by using the `-?` option.
   4. For example, run the command `Get-Command -?` to get help on the `Get-Command` command.
9. Powershell also uses aliases to simplify commands.
   1. For example, the `Get-Command` command has an alias of `gcm`.
   2. You can run the command `gcm` to get the same results as `Get-Command`.
   3. You can also run the command `gcm -?` to get the same results as `Get-Command -?`.
10. To see a list of all the aliases run the command `Get-Alias`.
11. Now that we have a basic understanding of powershell, let's start using it to perform some basic system administration tasks.

### Part 2 - Navigating Windows with Powershell

1. First, let's find out what directory we are currently in.
   1. Run the command `Get-Location` to find out what directory we are currently in.
   2. You should see something like `C:\Windows\System32`
2. Next lets go to our C: drive.
   1. Run the command `Set-Location C:\` to go to the C: drive.
   2. Run the command `Get-Location` to verify that we are in the C: drive.
   3. There are other ways to get to the C: drive.
   4. You can simply run the command `cd C:\` to go to the C: drive.
   5. You can also just type `cd /` linux style to go to the C: drive.
3. Windows Folder Structure
   1. The `C:\` drive has a specific folder structure, where `C:\` is the root directory.
   2. The `C:\Users` directory contains all the user directories. This folder contains one subfolder for each user that has logged onto the system at least once.
      1. `C:\Users\default` is the default user directory. This directory is used as a template for all new user directories.
      2. `C:\Users\Public` is the public user directory. This directory is used to share files between users.
   3. The `C:\Windows` directory contains all the windows files.
      1. The `C:\Windows\System32` & `C:\Windows\SysWOW64` directories contains all the system files. These files are used by the operating system. These folders store dynamic-link library (DLL) files that implement the core features of Windows and Windows API. Any time a program asks Windows to load a DLL file and do not specify a path, these folders are searched after program's own folder is searched.
      2. The `C:\Windows\Temp` directory contains all the temporary files.
      3. The `C:\Windows\Logs` directory contains all the log files.
   4. The `C:\Program Files` directory contains all the installed programs.
   5. The `C:\Program Files (x86)` directory contains all the installed 32-bit programs.
   6. The `C:\ProgramData` directory contains all the program data.
       1. Contains program data that is expected to be accessed by computer programs regardless of the user account in the context of which they run.
4. To see a list of all the files and directories in the current directory, run the command `Get-ChildItem`.
   1. You can also run the command `ls` to get the same results as `Get-ChildItem`.
   2. You can also run the command `dir` to get the same results as `Get-ChildItem`.
   3. You can also run the command `gci` to get the same results as `Get-ChildItem`.
5. The `Get-ChildItem` command will only show you all visible folders and files directly in the same directory you are currently in. What if you want to see hidden files and directories?
6. To see a list of all the files and directories in the current directory, including hidden files and directories, run the command `Get-ChildItem -Force`.
   1. You can also run the command `ls -Force` to get the same results as `Get-ChildItem -Force`.
   2. You can also run the command `dir -Force` to get the same results as `Get-ChildItem -Force`.
   3. You can also run the command `gci -Force` to get the same results as `Get-ChildItem -Force`.
7. Furthermore, your can view the contents of another directory by using the `-Path` option.
   1. For example, run the command `Get-ChildItem -Path C:\Windows` to view the contents of the `C:\Windows` directory.
   2. You can also run the command `ls -Path C:\Windows` to get the same results as `Get-ChildItem -Path C:\Windows`.
   3. You can also run the command `dir -Path C:\Windows` to get the same results as `Get-ChildItem -Path C:\Windows`.
   4. You can also run the command `gci -Path C:\Windows` to get the same results as `Get-ChildItem -Path C:\Windows`.
8. Next, lets look at how to create a directory using Powershell
   1. To create a new directory in the current directory, run the command `New-Item -ItemType Directory -Name Test`.
      1. `New-Item` is the command to create a new item.
      2. `-ItemType` Directory tells the New-Item command that we want to create a directory.
      3. `-Name Test` tells the New-Item command that we want to create a directory named Test.
   2. You can also run the command `mkdir Test` to get the same results as `New-Item -ItemType Directory -Name Test`.
   3. You can also run the command `md Test` to get the same results as `New-Item -ItemType Directory -Name Test`.
9. Change directory into the Test directory by running the command `cd Test`.
10. Next, let's create a new file in the Test directory.
    1. To create a new file in the current directory, run the command `New-Item -ItemType File -Name Test.txt`.
       1. `New-Item` is the command to create a new item.
       2. `-ItemType` File tells the New-Item command that we want to create a file.
       3. `-Name Test.txt` tells the New-Item command that we want to create a file named Test.txt.
    2. You can also run the command `ni Test.txt` to get the same results as `New-Item -ItemType File -Name Test.txt`.
11. This new file will not have any information in it. We can use multiple commands to add or append content to this file.
    1. Type `echo "Hello World" > Test.txt` to add the text `Hello World` to the file.
        1. `echo` is the command to print text to the screen.
        2. `>` is the redirect operator. It redirects the output of the command on the left to the file on the right.
        3. `"Hello World"` is the text we want to print to the screen.
        4. `Test.txt` is the file we want to print the text to.
    2. You can also use the `Set-Content` command to write to a file.
       1. Run the command `Set-Content Test.txt "New World"` to write the text `New World` to the file.
       2. You can also run the command `sc Test.txt "New World"` to get the same results as `Set-Content Test.txt "New World"`.
    3. To append text to the file, run the command `echo "Hello World" >> Test.txt`.
        1. `>>` is the append operator. It appends the output of the command on the left to the file on the right.
        2. If you accidentally use the `>` operator instead of the `>>` operator, you will overwrite the contents of the file, so be careful.
12. You can read the contents of the file by using the `Get-Content` command.
    1. Run the command `Get-Content Test.txt` to read the contents of the file.
    2. You can also run the command `gc Test.txt` to get the same results as `Get-Content Test.txt`.
    3. You can also run the command `type Test.txt` to get the same results as `Get-Content Test.txt`.
    4. You can also run the command `cat Test.txt` to get the same results as `Get-Content Test.txt`.
13. You can change the location of this file by moving or copying it to another folder.
    1. To copy the Test.txt file to the cyberarena home directory, run the command `Copy-Item Test.txt C:\Users\cyberarena\`.
       1. `Copy-Item` is the command to copy an item.
       2. `Test.txt` is the file we want to copy.
       3. `C:\Users\cyberarena\` is the directory we want to copy the file to.
    2. To move the file to the cyberarena home directory, run the command `Move-Item Test.txt C:\Users\cyberarena\`.
       1. `Move-Item` is the command to move an item.
       2. `Test.txt` is the file we want to move.
       3. `C:\Users\cyberarena\` is the directory we want to move the file to.
    3. You can also move directories and subdirectories.
       1. To do this use the `-Recurse` option.
       2. For example, run the command `Move-Item C:\Windows\Test C:\Users\cyberarena\ -Recurse` to move the Test directory and all its contents to the cyberarena home directory.
14. There are two ways to interact with command paths; relative path or absolute path.
    1. A relative path is a path that is relative to the current directory.
       1. For example: `Test.txt` is a relative path.
       2. If you are in the `C:\Windows` directory, then the relative path `Test.txt` will point to the file `C:\Windows\Test.txt`.
    2. An absolute path is a path that is relative to the root directory.
       1. For example: `C:\Windows\Test.txt` is an absolute path.
       2. The absolute path `C:\Windows\Test.txt` will always point to the file `C:\Windows\Test.txt` no matter what directory you are currently in.
15. One last tip that can help you with the Powershell command prompt. The space bar on your keyboard will auto-complete commands for you. For example, if you type `Get-` and then press the space bar, Powershell will auto-complete the command to `Get-Command`. It will also auto-complete file and directory names for you. For example, if you type `cd C:\Win` and then press the space bar, Powershell will auto-complete the command to `cd C:\Windows`.

Now that we can navigate the file system, let's move on to Windows permissions.

### Part 3 - Permissions

1. Let start by creating a new user named Alice
   1. Run the command `New-LocalUser -Name Alice -Password (ConvertTo-SecureString -AsPlainText "Password123" -Force)` to create a new user named Alice with the password `Password123`.
      1. The `New-LocalUser` command creates a new local user.
      2. The `-Name Alice` option tells the `New-LocalUser` command that we want to create a user named Alice.
      3. The `-Password (ConvertTo-SecureString -AsPlainText "Password123" -Force)` option tells the `New-LocalUser` command that we want to set the password to `Password123`.
         1. The `ConvertTo-SecureString` command converts the password to a secure string.
         2. The `-AsPlainText "Password123"` option tells the `ConvertTo-SecureString` command that we want to convert the password `Password123` to a secure string.
         3. The `-Force` option tells the `ConvertTo-SecureString` command that we want to convert the password `Password123` to a secure string without prompting the user for confirmation.
      4. You can also run the command `New-LocalUser Alice Password123` to get the same results as `New-LocalUser -Name Alice -Password (ConvertTo-SecureString -AsPlainText "Password123" -Force)`. This is a shortcut that will automatically convert the password to a secure string.
2. Now that we have the new user Alice, we need to give Alice group permissions
   1. Group permissions are a way to give multiple users the same permissions.
   2. For example, we can give Alice the same permissions as the `BUILTIN\Users` group.
   3. Run the command `Add-LocalGroupMember -Group "Users" -Member "Alice"` to add Alice to the `BUILTIN\Users` group.
      1. The `Add-LocalGroupMember` command adds a user to a local group.
      2. The `-Group "Users"` option tells the `Add-LocalGroupMember` command that we want to add a user to the `BUILTIN\Users` group.
      3. The `-Member "Alice"` option tells the `Add-LocalGroupMember` command that we want to add the user Alice to the `BUILTIN\Users` group.
      4. You can also run the command `Add-LocalGroupMember "Users" "Alice"` to get the same results as `Add-LocalGroupMember -Group "Users" -Member "Alice"`.
      5. You can also run the command `Add-LocalGroupMember "Users" "Alice"` to get the same results as `Add-LocalGroupMember -Group "Users" -Member "Alice"`.
3. To see a list of all the local groups, run the command `Get-LocalGroup`.
   1. You can also run the command `gl` to get the same results as `Get-LocalGroup`.
   2. You can also run the command `net localgroup` to get the same results as `Get-LocalGroup`.
4. To see a list of all the local users, run the command `Get-LocalUser`.
   1. You can also run the command `gu` to get the same results as `Get-LocalUser`.
   2. You can also run the command `net user` to get the same results as `Get-LocalUser`.
5. Let's find out what permissions we have on the file `Test.txt`.
   1. Run the command `Get-Acl Test.txt` to get the permissions on the file.

        ```powershell
        Path     Owner                  Access
        ----     -----                  ------
        Test.txt BUILTIN\Administrators NT AUTHORITY\SYSTEM Allow  FullControl…
        ```

   2. You can also run the command `Get-Acl Test.txt | Format-List` to get the permissions on the file in a list format.

        ```powershell
        Path   : Microsoft.PowerShell.Core\FileSystem::C:\Test\Test.txt
        Owner  : BUILTIN\Administrators
        Group  : CSEC1310-POWERS\None
        Access : NT AUTHORITY\SYSTEM Allow  FullControl
                 BUILTIN\Administrators Allow  FullControl
                 BUILTIN\Users Allow  ReadAndExecute, Synchronize
        Audit  :
        Sddl   : O:BAG:S-1-5-21-3150608446-1188364776-1620973061-513D:AI(A;ID;FA;;;SY)(A;ID;FA;;;BA)(A;ID;0x1200a9;;;BU)
        ```

   3. You can also run the command `Get-Acl Test.txt | fl` to get the permissions on the file in a list format.

        ```powershell
        Path     Owner                  Access
        ----     -----                  ------
        Test.txt BUILTIN\Administrators NT AUTHORITY\SYSTEM Allow  FullControl…
        ```

   4. You can also run the command `Get-Acl Test.txt | Format-Table` to get the permissions on the file in a table format.
   5. You can also run the command `Get-Acl Test.txt | ft` to get the permissions on the file in a table format.
   6. As you can see the Test.txt file has the following permissions.

        ```powershell
        Access : NT AUTHORITY\SYSTEM Allow  FullControl
                 BUILTIN\Administrators Allow  FullControl
                 BUILTIN\Users Allow  ReadAndExecute, Synchronize
        ```

       1. The `NT AUTHORITY\SYSTEM` user has `FullControl` permissions.
       2. The `BUILTIN\Administrators` user has `FullControl` permissions.
       3. The `BUILTIN\Users` user has `ReadAndExecute, Synchronize` permissions.
          1. This means that the `BUILTIN\Users` user can read and execute the file but cannot modify the file.
          2. This is the default permissions for all files and directories.
6. To change permissions of the file you can use `set-acl` command.
   1. Run the command `Set-Acl Test.txt -AccessControlType Deny -User BUILTIN\Users` to deny the `BUILTIN\Users` user access to the file.
   2. Run the command `Get-Acl Test.txt` to verify that the `BUILTIN\Users` user has been denied access to the file.

        ```powershell
        Path     Owner                  Access
        ----     -----                  ------
        Test.txt BUILTIN\Administrators NT AUTHORITY\SYSTEM Allow  FullControl…
        ```

   3. To change permissions of the file you can use `set-acl` command.
      1. Run the command `Set-Acl Test.txt -AccessControlType Deny -User BUILTIN\Users` to deny the `BUILTIN\Users` user access to the file.
7. Switch user to Alice by running the command `runas /user:Alice powershell`.
   1. You will be prompted for the password for Alice.
   2. Enter the password `Password123`.
   3. You will now be in a new powershell window as the user Alice.
8. Try to read the contents of the file by running the command `Get-Content Test.txt`.
   1. You should see an error message that says `Get-Content : Access to the path 'C:\Test\Test.txt' is denied.`.
   2. This is because the `BUILTIN\Users` user has been denied access to the file.
9. Close the new powershell window by running the command `exit` and return to the original window.
10. To delete the user Alice, run the command `Remove-LocalUser -Name Alice`.
    1. `Remove-LocalUser` is the command to remove a local user.
    2. `-Name Alice` option tells the `Remove-LocalUser` command that we want to remove the user Alice.
       1. You can also run the command `Remove-LocalUser Alice` to get the same results as `Remove-LocalUser -Name Alice`.
       2. You can also run the command `Remove-LocalUser "Alice"` to get the same results as `Remove-LocalUser -Name Alice`.
       3. You can also run the command `Remove-LocalUser "Alice"` to get the same results as `Remove-LocalUser -Name Alice`.
11. To delete the file Test.txt, run the command `Remove-Item Test.txt`.

### Part 4 - Process Commands

There may be times that you will need to view, start, stop, or kill a process. Powershell has commands to help you do this.

1. To view all processes in powershell, run the command `Get-Process`.

    ```powershell
     NPM(K)    PM(M)      WS(M)     CPU(s)      Id      SI    ProcessName
    ------    -----      -----     ------       --      --    -----------
      5        0.80       4.21     0.00         3488    0     AggregatorHost
     16        3.90      24.50     0.39         4680    2     ApplicationFrameHost
     13        3.00      12.16     0.06         2512    2     AzureArcSysTray
     12       10.43      22.18     7.80         1196    2     conhost
     20        1.88       6.22     0.62          436    0     csrss
     10        1.75       5.87     0.23          512    1     csrss
     15        1.93       6.71     0.88         1636    2     csrss
     15        3.42      19.92     0.41         6128    2     ctfmon
     10        1.77       9.00     0.02         2792    0     dllhost
     15        3.78      14.40     0.20         3296    0     dllhost
     18        3.28      14.20     0.19         6476    2     dllhost
     24       11.26      33.57     0.42          992    1     dwm
     42       26.50      71.18     5.33         3880    2     dwm
     65       25.84     104.41    10.16         3032    2     explorer
      7        1.90       5.33     0.12          524    2     fontdrvhost
      6        1.26       3.48     0.00          792    1     fontdrvhost
      6        1.29       3.51     0.05          800    0     fontdrvhost
     13       22.27      20.51     2.89         1680    0     GCEWindowsAgent
      8        1.75       6.40     0.03         2776    0     GoogleVssAgent
     13       24.03      20.96     2.36         1672    0     google_osconfig_agent
      0        0.06       0.01     0.00            0    0     Idle
     30       10.70      46.09     0.47         4916    1     LogonUI
     23        6.30      19.88    74.55          656    0     lsass
      4        0.43       1.73     0.00         3664    2     more.com
     14        2.92      11.04     0.16         3964    0     msdtc
    119       277.48     248.62 1,058.48        3040    0     MsMpEng
    ```

   1. You can also run the command `gps` to get the same results as `Get-Process`.
   2. You can also run the command `ps` to get the same results as `Get-Process`.
   3. You can also run the command `tasklist` to get the same results as `Get-Process`.
2. To view the first 10 processes in powershell, run the command `Get-Process | Select-Object -First 10`.
   1. You can also run the command `gps | Select-Object -First 10` to get the same results as `Get-Process | Select-Object -First 10`.
   2. You can also run the command `ps | Select-Object -First 10` to get the same results as `Get-Process | Select-Object -First 10`.
   3. You can also run the command `tasklist | Select-Object -First 10` to get the same results as `Get-Process | Select-Object -First 10`.
3. To view each process and the file used to start the process, run the command `Get-Process | Select-Object -Property ProcessName,Path`.
   1. You can also run the command `gps | Select-Object -Property ProcessName,Path` to get the same results as `Get-Process | Select-Object -Property ProcessName,Path`.
   2. You can also run the command `ps | Select-Object -Property ProcessName,Path` to get the same results as `Get-Process | Select-Object -Property ProcessName,Path`.
   3. You can also run the command `tasklist | Select-Object -Property ProcessName,Path` to get the same results as `Get-Process | Select-Object -Property ProcessName,Path`.
4. To start a process from powershell, run the `Start-Process` command.
   1. Run the command `Start-Process -FilePath "C:\Windows\System32\notepad.exe"` to start the notepad process.
      1. The `-FilePath "C:\Windows\System32\notepad.exe"` option tells the `Start-Process` command that we want to start the notepad process.
   2. You can also run the command `start notepad` to get the same results as `Start-Process -FilePath "C:\Windows\System32\notepad.exe"`.
   3. You can also run the command `notepad` to get the same results as `Start-Process -FilePath "C:\Windows\System32\notepad.exe"`.
   4. This will start the notepad.exe program.
5. To stop a process run the command `Stop-Process -Name "ProcessName"`.
   1. You can also run the command `kill -Name "ProcessName"` to get the same results as `Stop-Process -Name "ProcessName"`.
   2. You can also run the command `taskkill /IM "ProcessName"` to get the same results as `Stop-Process -Name "ProcessName"`.
   3. For example to stop notepad.exe, run the command `Stop-Process -Name "notepad"`.

### Part 5 - Service Commands

In Windows Services are used to run programs in the background. Services are similar to processes, but they are not tied to a specific user. Services are started when the computer boots up and run in the background until the computer is shut down.

1. To view services, run the command `Get-Service`.
   1. You can also run the command `gs` to get the same results as `Get-Service`.
   2. You can also run the command `sc query` to get the same results as `Get-Service`.
   3. You can also run the command `net start` to get the same results as `Get-Service`.
2. You can start a service by running the command `Start-Service -Name "ServiceName"`.
   1. You can also run the command `net start "ServiceName"` to get the same results as `Start-Service -Name "ServiceName"`.
   2. For example, to start the Windows Update service, run the command `Start-Service -Name "wuauserv"`.
      1. `Start-Service` is the command to start a service.
      2. `-Name "wuauserv"` option tells the `Start-Service` command that we want to start the Windows Update service.
3. You can stop a service with the `Stop-Service` command.
   1. You can also run the command `net stop "ServiceName"` to get the same results as `Stop-Service -Name "ServiceName"`.
   2. For example, to stop the Windows Update service, run the command `Stop-Service -Name "wuauserv"`.
      1. `Stop-Service` is the command to stop a service.
      2. `-Name "wuauserv"` option tells the `Stop-Service` command that we want to stop the Windows Update service.
4. You can restart a service with the `Restart-Service` command.
   1. You can also run the command `net stop "ServiceName" && net start "ServiceName"` to get the same results as `Restart-Service -Name "ServiceName"`.
   2. For example, to restart the Windows Update service, run the command `Restart-Service -Name "wuauserv"`.
      1. `Restart-Service` is the command to restart a service.
      2. `-Name "wuauserv"` option tells the `Restart-Service` command that we want to restart the Windows Update service.

### Part 7 - Network Commands

Windows has a ton if built in network commands. Here are a few of the most useful ones.

1. To view the network adapters on the system, run the command `Get-NetAdapter`.

    ```powershell
    Name        InterfaceDescription                 ifIndex Status       MacAddress             LinkSpeed
    ----        --------------------                 ------- ------       ----------             ---------
    Ethernet    Google VirtIO Ethernet Adapter             4 Up           42-01-0A-80-0F-D0       100 Gbps
    ```

   1. You can also run the command `Get-NetAdapter | Format-List` to get the same results as `Get-NetAdapter`.
   2. You can also run the command `Get-NetAdapter | fl` to get the same results as `Get-NetAdapter`.
   3. You can also run the command `Get-NetAdapter | Format-Table` to get the same results as `Get-NetAdapter`.
   4. You can also run the command `Get-NetAdapter | ft` to get the same results as `Get-NetAdapter`.
2. To view your IP address and network mask for the interface use the `Get-NetIPAddress` command.
   1. Run the command `Get-NetIPAddress` to view your IP address and network mask for the interface.
   2. You can also run the command `Get-NetIPAddress | Format-List` to get the same results as `Get-NetIPAddress`.
   3. You can also run the command `Get-NetIPAddress | fl` to get the same results as `Get-NetIPAddress`.
   4. You can also run the command `Get-NetIPAddress | Format-Table` to get the same results as `Get-NetIPAddress`.
   5. You can also run the command `Get-NetIPAddress | ft` to get the same results as `Get-NetIPAddress`.
   6. `ipconfig /all` will also show all interfaces.
3. Another important command is looking at the network statistics or what ports are open on the computer.
   1. To view the network statistics, run the command `Get-NetTCPConnection`.

        ```powershell
        LocalAddress                        LocalPort RemoteAddress                       RemotePort State       AppliedSetting OwningProcess
        ------------                        --------- -------------                       ---------- -----       -------------- -------------
        ::                                  49709     ::                                  0          Listen                     4216
        ::                                  49670     ::                                  0          Listen                     640
        ::                                  49669     ::                                  0          Listen                     2724
        ::                                  49668     ::                                  0          Listen                     2124
        ::                                  49666     ::                                  0          Listen                     1300
        ::                                  49665     ::                                  0          Listen                     504
        ::                                  49664     ::                                  0          Listen                     656
        ::                                  47001     ::                                  0          Listen                     4
        ::                                  5986      ::                                  0          Listen                     4
        ::                                  5985      ::                                  0          Listen                     4
        ::                                  3389      ::                                  0          Listen                     4928
        ::                                  445       ::                                  0          Listen                     4
        ::                                  135       ::                                  0          Listen                     880
        0.0.0.0                             49673     0.0.0.0                             0          Bound                      1680
        0.0.0.0                             49671     0.0.0.0                             0          Bound                      1672
        0.0.0.0                             49709     0.0.0.0                             0          Listen                     4216
        10.128.15.208                       49673     169.254.169.254                     80         Established Datacenter     1680
        10.128.15.208                       49671     169.254.169.254                     80         Established Datacenter     1672
        ```

      1. `LocalAddress` is the IP address of the local computer.
      2. `LocalPort` is the port number of the local computer.
      3. `RemoteAddress` is the IP address of the remote computer.
      4. `RemotePort` is the port number of the remote computer.
      5. `State` is the state of the connection.
      6. `AppliedSetting` is the setting applied to the connection.
      7. `OwningProcess` is the process that owns the connection.
4. You can also run the command `Get-NetTCPConnection | Format-List` to get the same results as `Get-NetTCPConnection`.

    ```powershell
    LocalAddress                        LocalPort RemoteAddress                       RemotePort State       AppliedSetting OwningProcess
    ------------                        --------- -------------                       ---------- -----       -------------- -------------
    ::                                  5355      ::                                  0          Listen                     4
    ::                                  3389      ::                                  0          Listen                     4928
    ::                                  445       ::                                  0          Listen                     4
    ::                                  135       ::                                  0          Listen                     880
    ```

5. To view the network statistics for UDP connections, run the command `Get-NetUDPEndpoint`.
6. Windows also comes bundled with a really good firewall. Here are a few of the commands to administer the firewall.
   1. To view the firewall rules, run the command `Get-NetFirewallRule`.
   2. To view the firewall rules in a list format, run the command `Get-NetFirewallRule | Format-List`.
   3. To view the firewall rules in a table format, run the command `Get-NetFirewallRule | Format-Table`.
   4. To add a firewall rule, run the command `New-NetFirewallRule`.
      1. Example: `New-NetFirewallRule -DisplayName "Block Port 80" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Block`.
         1. `-DisplayName "Block Port 80"` option tells the `New-NetFirewallRule` command that we want to create a firewall rule named "Block Port 80".
         2. `-Direction Inbound` option tells the `New-NetFirewallRule` command that we want to create a firewall rule for inbound traffic.
         3. `-LocalPort 80` option tells the `New-NetFirewallRule` command that we want to create a firewall rule for port 80.
         4. `-Protocol TCP` option tells the `New-NetFirewallRule` command that we want to create a firewall rule for TCP traffic.
         5. `-Action Block` option tells the `New-NetFirewallRule` command that we want to block traffic.
   5. To disable a rule, run the command `Set-NetFirewallRule`.
      1. Example: `Set-NetFirewallRule -DisplayName "Block Port 80" -Enabled False`.
         1. `-DisplayName "Block Port 80"` option tells the `Set-NetFirewallRule` command that we want to set the firewall rule named "Block Port 80".
         2. `-Enabled False` option tells the `Set-NetFirewallRule` command that we want to disable the firewall rule.
   6. To delete a rule, run the command `Remove-NetFirewallRule`.
      1. Example: `Remove-NetFirewallRule -DisplayName "Block Port 80"`.
         1. `-DisplayName "Block Port 80"` option tells the `Remove-NetFirewallRule` command that we want to remove the firewall rule named "Block Port 80".
