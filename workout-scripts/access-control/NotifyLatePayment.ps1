#Get email of late payment customer
$confirmation = Read-Host "Do you want to notify a late payment (y/N)?"
if ($confirmation -eq 'y') {
    [string]$email = Read-Host "Please enter the email of the person you would like to notify."
            #Send email to user
            Send-MailMessage -To $email  -From “msherman@trojanbricks.com” `
            -Subject “Late Payment Notification” `
            -Body “Hello, you have an outstanding payment. Please contact the payment office as soon as possible. Thank you.”  `
            -Credential (Get-Credential) -SmtpServer “<smtp server>” -Port 587
}

