[cmdletbinding()]
Param (
    [parameter()]
    [datetime]$EndDate = (Get-Date).AddMinutes(15),
    [parameter()]
    [string]$Message = "Time until attack!",
    [parameter()]
    [string]$Title = "Countdown To Attack",
    [parameter()]
    [ValidateSet('Black','Bold','DemiBold','ExtraBlack','ExtraBold','ExtraLight','Heavy','Light','Medium','Normal','Regular','SemiBold','Thin','UltraBlack','UltraBold','UltraLight')]
    [string]$FontWeight = 'Bold',
    [parameter()]
    [ValidateSet('Normal','Italic','Oblique')]
    [string]$FontStyle = 'Normal',
    [parameter()]
    [string]$FontSize = '25',
    [parameter()]
    [string]$MessageColor = 'White',
    [parameter()]
    [string]$CountDownColor = 'Red',
    [parameter()]
    [switch]$EndBeep,
    [parameter()]
    [switch]$EndFlash
    )

$rs = [RunspaceFactory]::CreateRunspace()
$rs.ApartmentState = “STA”
$rs.ThreadOptions = “ReuseThread”
$rs.Open()
$rs.SessionStateProxy.SetVariable('EndDate',$EndDate)
$rs.SessionStateProxy.SetVariable('Message',$Message)
$rs.SessionStateProxy.SetVariable('Title',$Title)
If ($PSBoundParameters['EndFlash']) {
    $rs.SessionStateProxy.SetVariable('EndBeep',$EndBeep)
}
If ($PSBoundParameters['EndBeep']) {
    $rs.SessionStateProxy.SetVariable('EndFlash',$EndFlash)
}
$rs.SessionStateProxy.SetVariable('FontWeight',$FontWeight)
$rs.SessionStateProxy.SetVariable('FontStyle',$FontStyle)
$rs.SessionStateProxy.SetVariable('FontSize',$FontSize)
$rs.SessionStateProxy.SetVariable('CountDownColor',$CountDownColor)
$rs.SessionStateProxy.SetVariable('MessageColor',$MessageColor)
$psCmd = {Add-Type -AssemblyName PresentationCore,PresentationFramework,WindowsBase}.GetPowerShell()
$psCmd.Runspace = $rs
$psCmd.Invoke()
$psCmd.Commands.Clear()
$psCmd.AddScript({

    #Load Required Assemblies
    Add-Type –assemblyName PresentationFramework
    Add-Type –assemblyName PresentationCore
    Add-Type –assemblyName WindowsBase

    #UI Build
    [xml]$xaml = @"
    <Window
        xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation'
        xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'
        x:Name='Window' ResizeMode = 'NoResize' WindowStartupLocation = 'CenterScreen' Title = '$title' Width = '860' Height = '321' ShowInTaskbar = 'True' WindowStyle = 'None' AllowsTransparency = 'True'>
        <Window.Background>
        <SolidColorBrush Color="Black"></SolidColorBrush>
        </Window.Background>
        <Grid x:Name = 'Grid' HorizontalAlignment="Stretch" VerticalAlignment = 'Stretch' ShowGridLines='false'  Background = 'Transparent'>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="2"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="2"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="2"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="*"/>
            </Grid.ColumnDefinitions>
            <Grid.RowDefinitions>
                <RowDefinition Height = '*'/>
                <RowDefinition Height = '*'/>
            </Grid.RowDefinitions>

            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '2'>
                <Label Width = '5' />
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '3'>
                <Label x:Name='d_MinuteLabel' FontSize = '$FontSize' FontWeight = '$FontWeight' Foreground = '$CountDownColor' FontStyle = '$FontStyle'/>
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '4'>
                <Label x:Name='MinuteLabel' FontWeight = '$FontWeight' Content = 'Minutes' FontSize = '$FontSize' FontStyle = '$FontStyle' Foreground = '$MessageColor' />
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '5'>
                <Label Width = '5' />
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '6'>
                <Label x:Name='d_SecondLabel' FontSize = '$FontSize' FontWeight = '$FontWeight' Foreground = '$CountDownColor' FontStyle = '$FontStyle' />
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '0' Grid.Column = '7'>
                <Label x:Name='SecondLabel' FontWeight = '$FontWeight' Content = 'Seconds' FontSize = '$FontSize' FontStyle = '$FontStyle' Foreground = '$MessageColor' />
            </Viewbox>
            <Viewbox VerticalAlignment = 'Stretch' HorizontalAlignment = 'Stretch' StretchDirection = 'Both' Stretch = 'Fill' Grid.Row = '1' Grid.ColumnSpan = '11'>
                <Label x:Name = 'TitleLabel' FontWeight = '$FontWeight' Content = '$Message' FontSize = '$FontSize' FontStyle = '$FontStyle' Foreground = '$MessageColor' />
            </Viewbox>
        </Grid>
    </Window>
"@

    $reader=(New-Object System.Xml.XmlNodeReader $xaml)
    $Global:Window=[Windows.Markup.XamlReader]::Load( $reader )

    #Collection of Colors for EndFlash
    $Colors = @(
        "Blue","Red","Yellow","Black","Green","Orange","Purple","White"

    )

    #Connect to Controls
    $TitleLabel = $Global:Window.FindName("TitleLabel")
    $d_MinuteLabel = $Global:Window.FindName("d_MinuteLabel")
    $MinuteLabel = $Global:Window.FindName("MinuteLabel")
    $d_SecondLabel = $Global:Window.FindName("d_SecondLabel")
    $SecondLabel = $Global:Window.FindName("SecondLabel")

    #Events
    $window.Add_MouseRightButtonUp({
        $this.close()
        })
    $Window.Add_MouseLeftButtonDown({
        $This.DragMove()
        })
    #Timer Event
    $Window.Add_SourceInitialized({
        Write-Verbose "Creating timer object"
        $Global:timer = new-object System.Windows.Threading.DispatcherTimer
        #Every 5 seconds
        Write-Verbose "Adding 1 second interval to timer object"
        $timer.Interval = [TimeSpan]"0:0:1.00"
        #Add Event Per Tick
        Write-Verbose "Adding Tick Event to timer object"
        $timer.Add_Tick({
            If ($EndDate -gt (Get-Date)) {
                $d_MinuteLabel.Content = ([datetime]"$EndDate" - (Get-Date)).Minutes
                $d_SecondLabel.Content = ([datetime]"$EndDate" - (Get-Date)).Seconds
            } Else {
                $d_MinuteLabel.Content = $d_SecondLabel.Content = 0
                $d_MinuteLabel.Foreground = $d_SecondLabel.Foreground = Get-Random -InputObject $Colors
                $MinuteLabel.Foreground = $SecondLabel.Foreground = Get-Random -InputObject $Colors
                If ($EndFlash) {
                    $TitleLabel.Foreground = Get-Random -InputObject $Colors
                }
                If ($EndBeep) {
                    [console]::Beep()
                }
            }
            })
        #Start Timer
        Write-Verbose "Starting Timer"
        $timer.Start()
        If (-NOT $timer.IsEnabled) {
            $Window.Close()
            }
        })
    $Window.ResizeMode = 'CanResizeWithGrip'
    $Window.Topmost = $False
    $Window.ShowDialog() | Out-Null
}).BeginInvoke() | out-null