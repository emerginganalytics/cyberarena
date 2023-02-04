$users = (dsquery group -name "Workout Users" | dsget group -members)
(Get-Acl C:\Users\workout\Desktop\Account_Control).access | ft IdentityReference | Out-File C:\Users\workout\file.txt
if($users -like '*Guymann*' -and     #used for testing users inside a group
$users -like '*Hansdown*' -and
$users -like '*Joeschmoe*' -and
$users -like '*Johndeer*' -and
$users -like '*Indigo Violet*' -and
(Get-Content C:\Users\workout\file.txt) -like '*Workout Users*') #used to test if group has permission
{
	$workout = @{"workout_id"=$env:WORKOUTID;
        "token"=$env:WORKOUTKEY0;
    }
    Invoke-WebRequest -UseBasicParsing "https://buildthewarrior.cybergym-eac-ualr.org/complete" -Method Post -Body $workout -ContentType "application/json"
}
Remove-Item C:\Users\workout\file.txt