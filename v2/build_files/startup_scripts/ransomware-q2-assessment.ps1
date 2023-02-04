$ProtectedFolder = "C:\Users\workout\Desktop"

$Protection = Get-MpPreference
$Protection.EnableControlledFolderAccess
$Protection.ControlledFolderAccessProtectedFolders
if($Protection.EnableControlledFolderAccess -eq 1 -and
$Protection.ControlledFolderAccessProtectedFolders -eq $ProtectedFolder)
{
    $workout = @{
        "workout_id"=$env:WORKOUTID;
        "token"=$env:WORKOUTKEY1;
    }
    Invoke-WebRequest -UseBasicParsing "$env:URL/complete" -Method Post -Body ($workout|ConvertTo-Json) -ContentType "application/json"
}