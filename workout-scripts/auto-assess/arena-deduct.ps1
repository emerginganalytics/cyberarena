$workout = @{"build_type"="arena"; "workout_id"=$env:WORKOUTID; "action"="deduct-points";}
Invoke-WebRequest -UseBasicParsing "https://buildthewarrior.cybergym-eac-ualr.org/complete" -Method Post -Body $workout -ContentType "application/json"
Remove-Item C:\Users\workout\file.txt