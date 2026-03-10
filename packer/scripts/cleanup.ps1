$ErrorActionPreference = "Continue"

Get-EventLog -LogName * | ForEach-Object { Clear-EventLog $_.Log -ErrorAction SilentlyContinue }

Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$Env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Users\*\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name wuauserv -ErrorAction SilentlyContinue

Remove-Item -Path "C:\Windows\Temp\packer-*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\script-*" -Recurse -Force -ErrorAction SilentlyContinue

$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
if ($adapter) {
    Set-NetIPInterface -InterfaceIndex $adapter.ifIndex -Dhcp Enabled -ErrorAction SilentlyContinue
    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue
}

Optimize-Volume -DriveLetter C -Defrag -ErrorAction SilentlyContinue
