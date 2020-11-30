function Invoke-Arena1-Deduct () {
  $deductworkout = @{"build_type"="arena"; "workout_id"=$env:WORKOUTID; "action"="deduct-points";}
  Invoke-WebRequest -UseBasicParsing "$env:URL/arena-functions" -Method Post -Body $deductworkout -ContentType "application/json"
  [pscustomobject]@{}
}