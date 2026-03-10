$ErrorActionPreference = "Stop"

$cloudbaseUrl = "https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi"
$installerPath = "C:\Windows\Temp\CloudbaseInitSetup.msi"
$installDir = "$Env:ProgramFiles\Cloudbase Solutions\Cloudbase-Init"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $cloudbaseUrl -OutFile $installerPath -UseBasicParsing

$msiArgs = @(
    "/i", "`"$installerPath`"",
    "/qn", "/norestart",
    "LOGGINGSERIALPORTNAME=COM1"
)
Start-Process msiexec.exe -ArgumentList $msiArgs -Wait -NoNewWindow
Start-Sleep -Seconds 5

if (-not (Test-Path $installDir)) {
    Write-Error "Cloudbase-Init installation failed"
    exit 1
}

$conf = @"
[DEFAULT]
username=Administrator
groups=Administrators
inject_user_password=true
first_logon_behaviour=no
bsdtar_path=$installDir\bin\bsdtar.exe
mtools_path=$installDir\bin\
log_dir=$installDir\log\
log_file=cloudbase-init.log
default_log_levels=comtypes=INFO,suds=INFO,iso8601=WARN,requests=WARN
local_scripts_path=$installDir\LocalScripts\
metadata_services=cloudbaseinit.metadata.services.configdrive.ConfigDriveService
plugins=cloudbaseinit.plugins.common.networkconfig.NetworkConfigPlugin,cloudbaseinit.plugins.common.sethostname.SetHostNamePlugin,cloudbaseinit.plugins.windows.extendvolumes.ExtendVolumesPlugin,cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin,cloudbaseinit.plugins.common.localscripts.LocalScriptsPlugin
allow_reboot=false
stop_service_on_exit=false
check_latest_version=false
"@

Set-Content -Path "$installDir\conf\cloudbase-init.conf" -Value $conf -Encoding UTF8

$unattendConf = @"
[DEFAULT]
username=Administrator
groups=Administrators
inject_user_password=true
first_logon_behaviour=no
bsdtar_path=$installDir\bin\bsdtar.exe
mtools_path=$installDir\bin\
log_dir=$installDir\log\
log_file=cloudbase-init-unattend.log
default_log_levels=comtypes=INFO,suds=INFO,iso8601=WARN,requests=WARN
local_scripts_path=$installDir\LocalScripts\
metadata_services=cloudbaseinit.metadata.services.configdrive.ConfigDriveService
plugins=cloudbaseinit.plugins.common.networkconfig.NetworkConfigPlugin,cloudbaseinit.plugins.common.sethostname.SetHostNamePlugin,cloudbaseinit.plugins.windows.extendvolumes.ExtendVolumesPlugin,cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin,cloudbaseinit.plugins.common.localscripts.LocalScriptsPlugin
allow_reboot=false
stop_service_on_exit=false
check_latest_version=false
"@

Set-Content -Path "$installDir\conf\cloudbase-init-unattend.conf" -Value $unattendConf -Encoding UTF8

$localScriptsDir = "$installDir\LocalScripts"
if (-not (Test-Path $localScriptsDir)) {
    New-Item -ItemType Directory -Path $localScriptsDir -Force | Out-Null
}

$winrmScript = @'
$maxRetries = 30
$retry = 0
while ($retry -lt $maxRetries) {
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
    if ($adapter) { break }
    Start-Sleep -Seconds 2
    $retry++
}
Restart-Service WinRM -Force -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "WinRM HTTP (5985)" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow -Profile Any -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "WinRM HTTPS (5986)" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow -Profile Any -ErrorAction SilentlyContinue
'@

Set-Content -Path "$localScriptsDir\enable-winrm.ps1" -Value $winrmScript -Encoding UTF8

Set-Service -Name "cloudbase-init" -StartupType Automatic -ErrorAction SilentlyContinue
Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
