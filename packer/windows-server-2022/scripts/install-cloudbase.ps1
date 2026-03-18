Write-Host "=== Installing Cloudbase-Init ==="

# Find the OEMDRV ISO (contains the MSI alongside autounattend.xml)
$oemdrvCD = Get-WmiObject -Class Win32_CDROMDrive |
    Where-Object { $_.VolumeName -eq "OEMDRV" } |
    Select-Object -First 1 -ExpandProperty Drive

if (-not $oemdrvCD) {
    throw "OEMDRV ISO not found. Cannot install Cloudbase-Init."
}

$installerPath = "$oemdrvCD\CloudbaseInitSetup_1_1_6_x64.msi"
if (-not (Test-Path $installerPath)) {
    throw "Cloudbase-Init MSI not found at $installerPath"
}

# Install silently (no sysprep at install time — we run sysprep via Packer shutdown_command)
Write-Host "Installing Cloudbase-Init ..."
$args = @(
    "/i", "`"$installerPath`"",
    "/qn", "/norestart",
    "/l*v", "C:\Windows\Temp\cloudbase-install.log",
    "LOGGINGSERIALPORTNAME=COM1"
)
Start-Process msiexec.exe -ArgumentList $args -Wait

$confDir = "C:\Program Files\Cloudbase Solutions\Cloudbase-Init\conf"

# Overwrite default configs with ours (uploaded by Packer file provisioner)
Write-Host "Applying Cloudbase-Init configuration ..."
Copy-Item -Force "C:\Windows\Temp\cloudbase-init.conf" "$confDir\cloudbase-init.conf"
Copy-Item -Force "C:\Windows\Temp\cloudbase-init-unattend.conf" "$confDir\cloudbase-init-unattend.conf"

Write-Host "=== Cloudbase-Init installed and configured ==="
exit 0
