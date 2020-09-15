Get-ADDefaultDomainPasswordPolicy | Out-File 'C:\Users\workout\file.txt'
if((Get-Content 'C:\Users\workout\file.txt')[2] -like '*True*' -and
(Get-Content 'C:\Users\workout\file.txt')[9] -like '*12*' -and
(Get-Content 'C:\Users\workout\file.txt')[7] -like '*365*')
{
    $workout = @{
        workout_id=$env:WORKOUTID;
        token=$env:WORKOUTKEY0;
    }| ConvertTo-Json
    $complete_url = -join("https://buildthewarrior", $env:DNS_SUFFIX, "/complete");
    Invoke-WebRequest -UseBasicParsing $complete_url -Method POST -Body $workout -ContentType "application/json"
}
Remove-Item 'C:\Users\workout\file.txt'