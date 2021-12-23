Import-Module activedirectory
New-ADGroup -Name "Executive Department" -SamAccountName ExecutiveDepartment -GroupCategory Security -GroupScope Global -DisplayName "Executive Department" -Path "CN=Users,DC=cybergym,DC=local" -Description "Executive Department Employees"
New-ADGroup -Name "Engineering Department" -SamAccountName EngineeringDepartment -GroupCategory Security -GroupScope Global -DisplayName "Engineering Department" -Path "CN=Users,DC=cybergym,DC=local" -Description "Engineering Department Employees"
New-ADGroup -Name "Accounting Department" -SamAccountName AccountingDepartment -GroupCategory Security -GroupScope Global -DisplayName "Accounting Department" -Path "CN=Users,DC=cybergym,DC=local" -Description "Accounting Department Employees"
New-ADGroup -Name "Human Resources Department" -SamAccountName HRDepartment -GroupCategory Security -GroupScope Global -DisplayName "Human Resources Department" -Path "CN=Users,DC=cybergym,DC=local" -Description "Human Resources Department Employees"
New-ADGroup -Name "Marketing Department" -SamAccountName MarketingDepartment -GroupCategory Security -GroupScope Global -DisplayName "Marketing Department" -Path "CN=Users,DC=cybergym,DC=local" -Description "Marketing Department Employees"
New-ADGroup -Name "Senior Staff" -SamAccountName SeniorStaff -GroupCategory Security -GroupScope Global -DisplayName "Senior Staff" -Path "CN=Users,DC=cybergym,DC=local" -Description "Senior Staff"
Add-ADGroupMember -Identity ExecutiveDepartment -Members lwolfe,jlewis,evolution
Add-ADGroupMember -Identity AccountingDepartment -Members msherman,kcurry
Add-ADGroupMember -Identity HRDepartment -Members jturn,cvargas,itworks
Add-ADGroupMember -Identity EngineeringDepartment -Members jbrown,jmcdaniel,itworks
Add-ADGroupMember -Identity MarketingDepartment -Members hblair,fcasey,evolution
Add-ADGroupMember -Identity SeniorStaff -Members lwolfe,jlewis,jbrown,jturn,hblair,cvargas