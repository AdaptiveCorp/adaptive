# ── Cloudbase-Init installation and configuration ────────────
# Enables Proxmox cloud-init support: on clone, the VM reads
# IP / gateway / DNS / hostname from Proxmox cloud-init config
# (delivered via ConfigDrive ISO).

Write-Host "=== Installing Cloudbase-Init ==="

$cloudbaseUrl = "https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi"
$installerPath = "C:\Windows\Temp\CloudbaseInitSetup.msi"
$installDir = "$Env:ProgramFiles\Cloudbase Solutions\Cloudbase-Init"

# ── Download ─────────────────────────────────────────────────
Write-Host "Downloading Cloudbase-Init..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $cloudbaseUrl -OutFile $installerPath -UseBasicParsing

# ── Install ──────────────────────────────────────────────────
Write-Host "Installing Cloudbase-Init..."
$msiArgs = @(
    "/i", "`"$installerPath`"",
    "/qn", "/norestart",
    "LOGGINGSERIALPORTNAME=COM1"
)
Start-Process msiexec.exe -ArgumentList $msiArgs -Wait -NoNewWindow

# Wait for install to complete
Start-Sleep -Seconds 5

if (-not (Test-Path $installDir)) {
    Write-Host "ERROR: Cloudbase-Init installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "Cloudbase-Init installed at $installDir"

# ── Configure cloudbase-init.conf (normal boot) ──────────────
$confPath = "$installDir\conf\cloudbase-init.conf"

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

# Proxmox uses ConfigDrive for cloud-init metadata
metadata_services=cloudbaseinit.metadata.services.configdrive.ConfigDriveService

# Plugins to run on boot
plugins=cloudbaseinit.plugins.common.networkconfig.NetworkConfigPlugin,cloudbaseinit.plugins.common.sethostname.SetHostNamePlugin,cloudbaseinit.plugins.windows.extendvolumes.ExtendVolumesPlugin,cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin,cloudbaseinit.plugins.common.localscripts.LocalScriptsPlugin

# Do not re-run plugins on every boot (only first boot after clone)
allow_reboot=false
stop_service_on_exit=false
check_latest_version=false
"@

Set-Content -Path $confPath -Value $conf -Encoding UTF8
Write-Host "Wrote $confPath"

# ── Configure cloudbase-init-unattend.conf (sysprep/OOBE boot) ──
$unattendConfPath = "$installDir\conf\cloudbase-init-unattend.conf"

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

Set-Content -Path $unattendConfPath -Value $unattendConf -Encoding UTF8
Write-Host "Wrote $unattendConfPath"

# ── LocalScript: re-enable WinRM after clone ─────────────────
# Ensures WinRM is functional after Cloudbase-Init configures the network
$localScriptsDir = "$installDir\LocalScripts"
if (-not (Test-Path $localScriptsDir)) {
    New-Item -ItemType Directory -Path $localScriptsDir -Force | Out-Null
}

$winrmScript = @'
# Re-enable WinRM after Cloudbase-Init network configuration
$maxRetries = 30
$retry = 0

# Wait for network adapter to be up
while ($retry -lt $maxRetries) {
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
    if ($adapter) { break }
    Start-Sleep -Seconds 2
    $retry++
}

# Restart WinRM to bind to the new IP
Restart-Service WinRM -Force -ErrorAction SilentlyContinue

# Ensure firewall rules are present
New-NetFirewallRule -DisplayName "WinRM HTTP (5985)" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow -Profile Any -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "WinRM HTTPS (5986)" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow -Profile Any -ErrorAction SilentlyContinue
'@

Set-Content -Path "$localScriptsDir\enable-winrm.ps1" -Value $winrmScript -Encoding UTF8
Write-Host "Wrote LocalScript: enable-winrm.ps1"

# ── Set Cloudbase-Init service to start automatically ────────
Set-Service -Name "cloudbase-init" -StartupType Automatic -ErrorAction SilentlyContinue

# ── Cleanup installer ───────────────────────────────────────
Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue

Write-Host "=== Cloudbase-Init configuration complete ==="
