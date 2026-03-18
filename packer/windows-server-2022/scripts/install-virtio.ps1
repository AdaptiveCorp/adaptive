Write-Host "=== Installing VirtIO drivers ==="

# Find VirtIO CD-ROM drive letter
$virtioCD = Get-WmiObject -Class Win32_CDROMDrive |
    Where-Object { $_.VolumeName -like "*virtio*" } |
    Select-Object -First 1 -ExpandProperty Drive

if (-not $virtioCD) {
    Write-Host "VirtIO ISO not found - listing available drives:"
    Get-WmiObject -Class Win32_CDROMDrive | ForEach-Object {
        Write-Host "  $($_.Drive) - $($_.VolumeName)"
    }
    throw "Cannot find VirtIO ISO. Aborting."
}

Write-Host "VirtIO ISO found on $virtioCD"

# vioscsi, viostor, NetKVM are already loaded via autounattend.xml (windowsPE pass)
# Only install additional drivers not included in the answer file
$drivers = @(
    "Balloon\2k22\amd64",
    "vioserial\2k22\amd64"
)

foreach ($driver in $drivers) {
    $path = "$virtioCD\$driver"
    if (Test-Path $path) {
        Write-Host "Installing $driver ..."
        pnputil.exe /add-driver "$path\*.inf" /install /subdirs
    }
}

# Install QEMU Guest Agent
$qemuMsi = "$virtioCD\guest-agent\qemu-ga-x86_64.msi"
if (Test-Path $qemuMsi) {
    Write-Host "Installing QEMU Guest Agent ..."
    Start-Process msiexec.exe -ArgumentList "/i `"$qemuMsi`" /qn /norestart" -Wait
    Set-Service -Name "QEMU-GA" -StartupType Automatic -ErrorAction SilentlyContinue
    Start-Service -Name "QEMU-GA" -ErrorAction SilentlyContinue
}

Write-Host "=== VirtIO installation complete ==="
exit 0
