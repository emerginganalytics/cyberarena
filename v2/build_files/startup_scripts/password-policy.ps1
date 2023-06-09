if((((Get-ADDefaultDomainPasswordPolicy).MinPasswordLength) -eq 12) -and (((Get-ADDefaultDomainPasswordPolicy).MaxPasswordAge.Days) -eq 365) -and (((Get-ADDefaultDomainPasswordPolicy).ComplexityEnabled) -eq "True")){

    Write-Output "True"

}
else{
    Write-Output "False"
}