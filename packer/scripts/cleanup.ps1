# ── Template cleanup ─────────────────────────────────────────
# Prepares the VM for conversion to a Proxmox template.

Write-Host "=== Cleaning up for template ==="

# ── Clear event logs ─────────────────────────────────────────
Write-Host "Clearing event logs..."
Get-EventLog -LogName * | ForEach-Object { Clear-EventLog $_.Log -ErrorAction SilentlyContinue }

# ── Remove temp files ────────────────────────────────────────
Write-Host "Removing temp files..."
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$Env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Users\*\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# ── Clear Windows Update cache ───────────────────────────────
Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name wuauserv -ErrorAction SilentlyContinue

# ── Remove Packer build artifacts ────────────────────────────
Remove-Item -Path "C:\Windows\Temp\packer-*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\script-*" -Recurse -Force -ErrorAction SilentlyContinue

# ── Reset network config (Cloudbase-Init will reconfigure on clone) ──
Write-Host "Removing static IP (will be set by Cloudbase-Init on clone)..."
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
if ($adapter) {
    # Switch back to DHCP so the template is clean
    Set-NetIPInterface -InterfaceIndex $adapter.ifIndex -Dhcp Enabled -ErrorAction SilentlyContinue
    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue
}

# ── Optimize disk ────────────────────────────────────────────
Write-Host "Optimizing disk..."
Optimize-Volume -DriveLetter C -Defrag -ErrorAction SilentlyContinue

Write-Host "=== Cleanup complete — ready to convert to template ==="
