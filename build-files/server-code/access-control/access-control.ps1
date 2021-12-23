#Access-Control Permission Check and Assessment Script


#Folder Locations
$ContractsFolder = "C:\Company Data\Federal Contracts"
$BatchFolder = "C:\Batch"
$WebFolder = "C:\inetpub\wwwroot\TrojanBricks"

#Users and Permissions for Folders
$ContractsUsers = (Get-Acl -Path $ContractsFolder).Access.IdentityReference
$WebUsers = (Get-Acl -Path $WebFolder).Access.IdentityReference
$BatchUsers = (Get-Acl -Path $BatchFolder).Access.IdentityReference

#Assessment Variables
$Count = 0
$Url = "https://buildthewarrior" + $Env:DNS_SUFFIX + "/complete"

#Check Contracts Folder for AwesomeITUser
foreach ($User in $ContractsUsers){
    $CheckPermissions = (Get-Acl $ContractsFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
       if($User -eq "CYBERGYM\AwesomeITUser") {
	    $Count = 0
            break
       }
       else {
            $Count += 1
       }
    }
}

#Check Web Folder for Harold Blair
foreach ($User in $WebUsers){
    $CheckPermissions = (Get-Acl $WebFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
       if($User -eq "CYBERGYM\hblair") {
            $Count = 0
            break
       }
       elseif(($User -ne "BUILTIN\IIS_IUSRS") -and ($User -ne "NT AUTHORITY\IUSR")) {
            $Count += 1
       }
    }
}
#Check Batch Folder for Lola Wolfe
foreach ($User in $BatchUsers){
    $CheckPermissions = (Get-Acl $BatchFolder).Access | Where-Object AccessControlType -eq "Allow" `
    | Where-Object IdentityReference -eq $User
    if ($CheckPermissions) {
       if($User -eq "CYBERGYM\lwolfe") {
            $Count = 0
	        break
       }
       else {
            $Count += 1
       }
    }
}
#Workout Environment Variables
$request_body = @{
    "workout_id"= $Env:WORKOUTID
    "token"= $Env:WORKOUTKEY0
} | ConvertTo-Json

#If all three users have been removed, send completion result
if ($Count -eq 10) {
    Write-Host "Workout Completed!"
    Invoke-WebRequest -UseBasicParsing $Url -ContentType "application/json" -Method POST -Body $request_body
}
else
{
    Write-Host "Found User with Access!"
    & "C:\Users\Gymboss\Temp\attack.ps1"
}
Start-Sleep -Seconds 10