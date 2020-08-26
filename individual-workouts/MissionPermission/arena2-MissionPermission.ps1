#Arena 2 Permission Auto-checker

#folder being checked
$folder = "C:\Users\workout\Desktop\Protect_Me"
#debugging document
$debugger = "C:\Users\workout\Documents\permissionChecks\debugger.txt"
#flag carrying file
$flag_file = "C:\Users\workout\Desktop\PermissionFlag.txt"
#flag
$flag = "Flag = Cybergym{SecuredTheRickRoll}"
#pulling info on the folder and scrubbing the name input
$all_info = (get-acl $folder) | select -expandproperty access | where-object { ('NT AUTHORITY\SYSTEM','BUILTIN\Administrators','CYBERGYM-RANSOM\workout' -notcontains $_.identityreference) } | select-object @{ name = 'Identity'; expression = { $_.identityreference -replace "\w+\\(.+)", '$1' } }, filesystemrights, accesscontroltype
#number of users that shouldn't have access still
$extra_users = 0

foreach($user in $all_info){

    #checks if current user is allowed in the folder
    $info_allow = $all_info | where-object {$_.identity -eq ($user | %{$_.identity})} | where-object {$_.accesscontroltype -eq "Allow"}
    #checks is current user is denied in the folder
    $info_deny = $all_info | where-object {$_.identity -eq ($user | %{$_.identity})} | where-object {$_.accesscontroltype -eq "Deny"}

    #checks if the user doesn't have an allow and deny entry with the same name
    if(($info_allow | % {$_.identity}) -ne ($info_deny | % {$_.identity})){
        add-content $debugger ($info_allow | %{"User '$($_.identity)' has access to the folder '$folder'"})
        $extra_users += 1
    }
}

#flag giver
if($extra_users -eq 0){
    
    #check for flag file, if it doesn't exist create it and print the flag in it
    if(test-path $flag_file -pathType leaf){
        add-content $flag_file $flag
    }else{
        new-item $flag_file
        set-content $flag_file $flag
    }
}