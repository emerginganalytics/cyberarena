#Access-Control Restore Script


#Folder Locations
$ContractsFolder = "C:\Company Data\Federal Contracts"
$BatchFolder = "C:\Batch"
$WebFolder = "C:\inetpub\wwwroot\TrojanBricks"

#Restore Permissions for AwesomeITUser in Contracts Folder
$Permission = (Get-Acl $ContractsFolder).Access | Where-Object{$_.IdentityReference -match "CYBERGYM\AwesomeITUser"} `
| Select-Object IdentityReference,FileSystemRights
if ($Permission){
    $Permission | ForEach-Object {Write-Host "User $($_.IdentityReference) has '$($_.FileSystemRights)' rights on folder $ContractsFolder"}
}
else {
    $acl = Get-Acl -Path $ContractsFolder
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("CYBERGYM\AwesomeITUser","FullControl","Allow")
    $acl.SetAccessRule($AccessRule)
    $acl | Set-Acl -Path $ContractsFolder
}

#Restore Permissions for Harold Blair in Web Folder
$Permission = (Get-Acl $WebFolder).Access | Where-Object{$_.IdentityReference -match "CYBERGYM\hblair"} `
| Select-Object IdentityReference,FileSystemRights
if ($Permission){
    $Permission | ForEach-Object {Write-Host "User $($_.IdentityReference) has '$($_.FileSystemRights)' rights on folder $WebFolder"}
}
else {
    $acl = Get-Acl -Path $WebFolder
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("CYBERGYM\hblair","FullControl","Allow")
    $acl.SetAccessRule($AccessRule)
    $acl | Set-Acl -Path $WebFolder
}

#Restore Permissions for Lola Wolfe in Batch Folder
$Permission = (Get-Acl $BatchFolder).Access | Where-Object{$_.IdentityReference -match "CYBERGYM\lwolfe"} `
| Select-Object IdentityReference,FileSystemRights
if ($Permission){
    $Permission | ForEach-Object {Write-Host "User $($_.IdentityReference) has '$($_.FileSystemRights)' rights on folder $BatchFolder"}
}
else {
    $acl = Get-Acl -Path $BatchFolder
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("CYBERGYM\lwolfe","FullControl","Allow")
    $acl.SetAccessRule($AccessRule)
    $acl | Set-Acl -Path $BatchFolder
}

#Clean Slate for Contracts Folder
Get-ChildItem -Path "C:\Company Data\Federal Contracts" * -Recurse | Remove-Item -Confirm:$false
Copy-Item -Path "C:\Users\Gymboss\Temp\Restore\Federal Site Contract.docx" -Destination "C:\Company Data\Federal Contracts"

#Clean Slate for Web Folder
Remove-Item -Path "C:\inetpub\wwwroot\TrojanBricks\templates\index.html" -Confirm:$false
Copy-Item -Path "C:\Users\Gymboss\Temp\Restore\index.html" -Destination "C:\inetpub\wwwroot\TrojanBricks\templates"

Remove-Item -Path "C:\inetpub\wwwroot\TrojanBricks\static\css\base.css" -Confirm:$false
Copy-Item -Path "C:\Users\Gymboss\Temp\Restore\base.css" -Destination "C:\inetpub\wwwroot\TrojanBricks\static\css"

Remove-Item -Path "C:\inetpub\wwwroot\TrojanBricks\static\images\scam_alert.jpg" -Confirm:$false
Copy-Item -Path "C:\Users\Gymboss\Temp\Restore\Brick_Background.png" -Destination "C:\inetpub\wwwroot\TrojanBricks\static\images"

#Delete Google Chrome Cache for updated images and files
taskkill /F /IM "chrome.exe"
Start-Sleep -Seconds 5
 $Items = @('Archived History',
            'Cache\*',
            'Code Cache\*',
            'GPUCache\*'
            'Cookies',
            'History',
            'Web History',
            'Storage\*',
            'Shortcuts',
            'blob_storage',
            'Login Data',
            'Top Sites',
            'Visited Links',
            'Web Data')
$Folder = "$($env:LOCALAPPDATA)\Google\Chrome\User Data\Default"
$Items | ForEach-Object {
    if (Test-Path "$Folder\$_") {
        Remove-Item "$Folder\$_" -Recurse
    }
}
#Clean Slate for Batch Folder
Remove-Item -Path "C:\Batch\NotifyLatePayment.ps1" -Confirm:$false
Copy-Item -Path "C:\Users\Gymboss\Temp\Restore\NotifyLatePayment.ps1" -Destination "C:\Batch"

#Change Wallpaper to Default Windows 10
function Set-Wallpaper {
    param (
        [string]$Path,
        [ValidateSet('Tile', 'Center', 'Stretch', 'Fill', 'Fit', 'Span')]
        [string]$Style = 'Fill'
    )

    begin {
        try {
            Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                using Microsoft.Win32;
                namespace Wallpaper
                {
                    public enum Style : int
                    {
	                    Tile, Center, Stretch, Fill, Fit, Span, NoChange
                    }

                    public class Setter
                    {
	                    public const int SetDesktopWallpaper = 20;
	                    public const int UpdateIniFile = 0x01;
	                    public const int SendWinIniChange = 0x02;
	                    [DllImport( "user32.dll", SetLastError = true, CharSet = CharSet.Auto )]
	                    private static extern int SystemParametersInfo ( int uAction, int uParam, string lpvParam, int fuWinIni );
	                    public static void SetWallpaper ( string path, Wallpaper.Style style )
                        {
		                    SystemParametersInfo( SetDesktopWallpaper, 0, path, UpdateIniFile | SendWinIniChange );
		                    RegistryKey key = Registry.CurrentUser.OpenSubKey( "Control Panel\\Desktop", true );
		                    switch( style )
		                    {
			                    case Style.Tile :
			                    key.SetValue( @"WallpaperStyle", "0" ) ;
			                    key.SetValue( @"TileWallpaper", "1" ) ;
			                    break;
			                    case Style.Center :
			                    key.SetValue( @"WallpaperStyle", "0" ) ;
			                    key.SetValue( @"TileWallpaper", "0" ) ;
			                    break;
			                    case Style.Stretch :
			                    key.SetValue( @"WallpaperStyle", "2" ) ;
			                    key.SetValue( @"TileWallpaper", "0" ) ;
			                    break;
			                    case Style.Fill :
			                    key.SetValue( @"WallpaperStyle", "10" ) ;
			                    key.SetValue( @"TileWallpaper", "0" ) ;
			                    break;
			                    case Style.Fit :
			                    key.SetValue( @"WallpaperStyle", "6" ) ;
			                    key.SetValue( @"TileWallpaper", "0" ) ;
			                    break;
			                    case Style.Span :
			                    key.SetValue( @"WallpaperStyle", "22" ) ;
			                    key.SetValue( @"TileWallpaper", "0" ) ;
			                    break;
			                    case Style.NoChange :
			                    break;
		                    }
		                    key.Close();
	                    }
                    }
                }
"@
        } catch {}

        $StyleNum = @{
            Tile = 0
            Center = 1
            Stretch = 2
            Fill = 3
            Fit = 4
            Span = 5
        }
    }

    process {
        [Wallpaper.Setter]::SetWallpaper($Path, $StyleNum[$Style])
        Start-Sleep -Seconds 1
        [Wallpaper.Setter]::SetWallpaper($Path, $StyleNum[$Style])
    }
}

Set-WallPaper -Path 'C:\Windows\Web\Wallpaper\Windows\img0.jpg' -Style Fill
