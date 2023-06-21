$userList = @(
    @{Username="ackbar"; FullName="Admiral Ackbar"},
    @{Username="c3po"; FullName="C-3PO"},
    @{Username="chewie"; FullName="Chewbacca"},
    @{Username="darth"; FullName="Anakin Skywalker"},
    @{Username="dooku"; FullName="Count Dooku"},
    @{Username="grevious"; FullName="General Grevious"},
    @{Username="han"; FullName="Han Solo"},
    @{Username="jarjar"; FullName="Jar-Jar Binks"},
    @{Username="jyn"; FullName="Jyn Erso"},
    @{Username="lando"; FullName="Lando Calrissian"},
    @{Username="luke"; FullName="Luke Skywalker"},
    @{Username="mace"; FullName="Mace Windu"},
    @{Username="mon"; FullName="Mon Mothma"},
    @{Username="obi"; FullName="Obi-Wan Kenobi"},
    @{Username="orson"; FullName="Orson Krennic"},
    @{Username="r2d2"; FullName="R2D2 (Artoo-Detoo)"},
    @{Username="sabrine"; FullName="Sabrine Wren"},
    @{Username="watto"; FullName="Watto"},
    @{Username="wedge"; FullName="Wedge Antilles"},
    @{Username="yoda"; FullName="Yoda"}
)

$group_accounts = @{
    "Rebel Alliance Leaders" = @("han", "orson", "grevious", "ackbar", "leia", "mon")
    "Pilots" = @("jarjar", "darth", "dooku", "chewie", "han", "lando", "luke", "wedge")
    "Engineers" = @("watto", "c3po", "jyn", "sabrine")
    "Jedi Council" = @("luke", "r2d2", "darth", "dooku", "obi", "yoda")
}

$folder_privileges = @{
    'C:\Rebel Forces\Alliance Budgets' = @{
        'groups' = @{
            'Rebel Alliance Leaders' = 'ReadAndExecute'
        }
        'users' = @{
            'watto' = 'FullControl'
            'han' = 'Modify'
            'ackbar' = 'FullControl'
        }
    }
    'C:\Rebel Forces\Design Blueprints' = @{
        'groups' = @{
            'Engineers' = 'FullControl'
        }
        'users' = @{
            'c3po' = 'ReadAndExecute'
            'jyn' = 'FullControl'
            'sabrine' = 'ReadAndExecute'
        }
    }
    'C:\Rebel Forces\Flight Logs' = @{
        'groups' = @{
            'Engineers' = 'ReadAndExecute'
        }
        'users' = @{
            'jarjar' = 'FullControl'
            'darth' = 'FullControl'
            'chewie' = 'ReadAndExecute'
            'han' = 'FullControl'
            'lando' = 'Modify'
        }
    }
    'C:\Rebel Forces\Maintenance Schedules' = @{
        'groups' = @{
            'Engineers' = 'FullControl'
        }
        'users' = @{
            'sabrine' = 'Modify'
        }
    }
    'C:\Rebel Forces\Mission Reports' = @{
        'groups' = @{
            'Jedi Council' = 'FullControl'
            'Rebel Alliance Leaders' = 'FullControl'
            'Pilots' = 'ReadAndExecute'
        }
        'users' = @{
            'c3po' = 'ReadAndExecute'
            'jyn' = 'FullControl'
            'sabrine' = 'ReadAndExecute'
        }
    }
    'C:\Rebel Forces\Navigational Charts' = @{
        'groups' = @{}
        'users' = @{
            'jarjar' = 'FullControl'
            'chewie' = 'ReadAndExecute'
            'han' = 'FullControl'
            'lando' = 'Modify'
        }
    }
    'C:\Rebel Forces\Starship Specifications' = @{
        'groups' = @{
            'Pilots' = 'FullControl'
            'Engineers' = 'FullControl'
        }
        'users' = @{
            'orson' = 'FullControl'
            'grevious' = 'Modify'
            'luke' = 'ReadAndExecute'
        }
    }
    'C:\Rebel Forces\Strategic Plans' = @{
        'groups' = @{
            'Jedi Council' = 'FullControl'
        }
        'users' = @{
            'ackbar' = 'FullControl'
            'jyn' = 'ReadAndExecute'
            'r2d2' = 'Modify'
            'obi' = 'FullControl'
        }
    }
    'C:\Rebel Forces\Technical Documentation' = @{
        'groups' = @{}
        'users' = @{
            'wedge' = 'Modify'
            'yoda' = 'FullControl'
            'han' = 'Modify'
            'luke' = 'FullControl'
        }
    }
}


#
# Delete the access control setup
#
$response = Read-Host "Do you want to delete the access control setup at this time? (Y/n)"
if ($response -ne 'n' -and $response -ne 'N') {
    #
    # Remove Permissions for groups
    #
    foreach ($folderPath in $folder_privileges) {
        # Get the current ACL
        $acl = Get-Acl -Path $folderPath

        # Remove all the access rules
        $acl.SetAccessRuleProtection($true, $false)
        $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }

        Set-Acl -Path $folderPath -AclObject $acl
    }
    #
    # Loop through each user in the list and delete the users
    #
    foreach ($user in $userList) {
        # Check if the user exists
        if (Get-LocalUser -Name $user.Username) {
            # Delete the user
            Remove-LocalUser -Name $user.Username
        }
    }

    # Loop through and remove the groups
    foreach ($item in $group_accounts.GetEnumerator()) {
        Remove-LocalGroup -Name $item.Key
    }
}

#
# Create
#
$response = Read-Host "Do you want to create the access control setup at this time? (Y/n)"

# Check if the response was 'n' or 'N'
if ($response -ne 'n' -and $response -ne 'N') {
    # Loop through each user in the list
    foreach ($user in $userList) {
        # Specify the password
        $Password = ConvertTo-SecureString "MayThe4thBeWithYou!" -AsPlainText -Force

        # Create the user
        New-LocalUser $user.Username -Password $Password -FullName $user.FullName -Description ""
    }

    # Add users to groups
    foreach ($item in $group_accounts.GetEnumerator()) {
        if (-not (Get-LocalGroup -Name $item.Key -ErrorAction SilentlyContinue)) {
            New-LocalGroup -Name $item.Key
        }
        foreach ($user in $item.Value) {
            Add-LocalGroupMember -Group $item.Key -Member $user
        }
    }

    # Create folder permissions
    foreach ($folder_item in $folder_privileges.GetEnumerator()) {
        if (!(Test-Path $folder_item.Key)) {
            New-Item -ItemType Directory -Path $folder_item.Key
        }
        foreach ($item in $folder_item.Value.groups.GetEnumerator()) {
            $acl = Get-Acl -Path $folder_item.Key
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($item.Key, $item.Value, "ContainerInherit,ObjectInherit", "None", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl -Path $folder_item.Key -AclObject $acl
        }
        foreach ($item in $folder_item.Value.users.GetEnumerator()) {
            $acl = Get-Acl -Path $folder_item.Key
            Write-Host $item.Key + " " + $item.Value
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($item.Key, $item.Value, "ContainerInherit,ObjectInherit", "None", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl -Path $folder_item.Key -AclObject $acl
        }
    }
}