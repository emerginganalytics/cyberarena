<#
    Powershell Script to check Mission: Permission Status
#>

$Target_Folder = 'C:\Users\workout\Desktop\Protect_Me'
$Users = (Get-Acl -Path $Target_Folder).Access.IdentityReference
$Count = 0

Foreach ($User in $Users){
    $check_permissions = (Get-Acl $Target_Folder).Access | Where-Object AccessControlType -EQ "Allow" | Where-Object IdentityReference -EQ $User
    If ($check_permissions) {
       If(($User -ne "WINDOWS-SERVER-\workout") -and ($User -ne "NT AUTHORITY\SYSTEM") -and ($User -ne "WINDOWS-SERVER-\Administrators") -and ($User -ne "BUILTIN\Administrators")) {
            # Write-Host "CRITICAL ERROR:"
            # $check_permissions | % {Write-Host "User $($_.IdentityReference) has '$($_.FileSystemRights)' rights on folder $Target_folder"} 
            Break
       }
       Else {
            $Count += 1
       }
    } # If check_permissions -eq false
    Else {
       Write-Host "$User Doesn't have any permissions on $Target_Folder"
    } 
}

If ($Count -eq 4) {
    Write-Host "[+] Workout Complete!"
    Write-Host "[*] Posting Results ..."
    python C:\Data\MissionPermission\Mission_Permission.py 10.128.0.20 "Windows Secure!"
}
