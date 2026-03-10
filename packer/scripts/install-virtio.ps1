# ── VirtIO drivers installation ──────────────────────────────
# Installs remaining VirtIO drivers + QEMU Guest Agent.
# The core drivers (vioscsi, viostor, NetKVM) are loaded during
# Windows Setup via autounattend.xml DriverPaths.

Write-Host "=== Installing VirtIO drivers ==="

# Find the VirtIO ISO drive
$virtioCD = Get-WmiObject -Class Win32_CDROMDrive |
    Where-Object { $_.VolumeName -like "*virtio*" } |
    Select-Object -First 1 -ExpandProperty Drive

if (-not $virtioCD) {
    # Fallback: try all CD drives
    $virtioCD = Get-WmiObject -Class Win32_CDROMDrive | ForEach-Object {
        if (Test-Path "$($_.Drive)\guest-agent") { $_.Drive }
    } | Select-Object -First 1
}

if ($virtioCD) {
    Write-Host "VirtIO ISO found on $virtioCD"

    # Additional drivers (core ones already loaded by autounattend)
    $drivers = @(
        "Balloon\2k22\amd64",
        "vioserial\2k22\amd64",
        "viorng\2k22\amd64",
        "pvpanic\2k22\amd64"
    )

    foreach ($driver in $drivers) {
        $driverPath = "$virtioCD\$driver"
        if (Test-Path $driverPath) {
            Write-Host "Installing $driver..."
            pnputil.exe /add-driver "$driverPath\*.inf" /install /subdirs 2>&1 | Out-Null
        }
    }

    # QEMU Guest Agent
    $qemuAgent = "$virtioCD\guest-agent\qemu-ga-x86_64.msi"
    if (Test-Path $qemuAgent) {
        Write-Host "Installing QEMU Guest Agent..."
        Start-Process msiexec.exe -ArgumentList "/i `"$qemuAgent`" /qn /norestart" -Wait -NoNewWindow
    }

    Write-Host "VirtIO drivers installed"
} else {
    Write-Host "WARNING: VirtIO ISO not found" -ForegroundColor Yellow
    Get-WmiObject -Class Win32_CDROMDrive | ForEach-Object {
        Write-Host "  CD: $($_.Drive) — $($_.VolumeName)"
    }
}

# Enable QEMU Guest Agent service
Set-Service -Name "QEMU-GA" -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name "QEMU-GA" -ErrorAction SilentlyContinue

Write-Host "=== VirtIO installation complete ==="
