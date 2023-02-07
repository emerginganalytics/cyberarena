if((((Get-ADDefaultDomainPasswordPolicy).MinPasswordLength) -eq 12) -and (((Get-ADDefaultDomainPasswordPolicy).MaxPasswordAge.Days) -eq 365) -and (((Get-ADDefaultDomainPasswordPolicy).ComplexityEnabled) -eq "True")){

    $workout = @{
        workout_id=$env:WORKOUTID;
        token=$env:WORKOUTKEY0;
    }| ConvertTo-Json
    $complete_url = -join("https://buildthewarrior", $env:DNS_SUFFIX, "/complete");
    Invoke-WebRequest -UseBasicParsing $complete_url -Method POST -Body $workout -ContentType "application/json"

}
