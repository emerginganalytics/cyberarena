# Mission Permission Student Instructions

## Introduction
In this exercise, you will learn how to manage file permissions in the Windows operating system to enhance the security of your computer's file systems. File permissions dictate who can access and modify specific files. When a file is created or added to your computer, it's assigned a set of rules that determine which users, programs, or groups can interact with it. For instance, consider the "Program Files" folder on Windows machines. While any user can view its contents, making changes requires membership in the Administrator group.

## Getting Started: Logging into Your Computer
To begin, access the Guacamole web server using the provided username and password from your Cyber Gym student landing page. If a screen doesn't load immediately, try refreshing the page; you'll be logged in automatically.

## Your Task
The security team has detected a security issue in the system logs. A folder named ".. Desktop\Protect_Me\" contains critical information and has been granted read, write, and execute permissions for all users, including anonymous users and an unauthorized user. Your mission is to rectify this by restricting access to only authorized users.

## Steps to Accomplish Your Mission
1. To assess permissions, right-click the folder or file and select "Properties," then go to the "Security" tab.
2. In the top section, you'll find a list of users and user groups with access to the folder. Identify users who should not have access.
3. Click the "Edit" button to adjust permissions. Remove access for users who shouldn't be allowed.

## Important Note
Do not modify permissions for the following users/user groups to ensure proper system functionality:
- Windows-Server-\workout
- NT Authority\System
- Windows-Server-\Administrators
- Builtin\Administrators

By completing this exercise, you'll gain valuable knowledge about managing file permissions on Windows systems and contribute to enhancing system security.
