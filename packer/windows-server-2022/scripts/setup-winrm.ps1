Write-Host "=== Configuring WinRM for Ansible ==="

# Ensure WinRM service is running and set to auto-start
Set-Service -Name WinRM -StartupType Automatic
Start-Service -Name WinRM

# Enable PowerShell remoting
Enable-PSRemoting -Force

# Allow Basic auth (used by ansible pywinrm)
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true

# Allow unencrypted transport (lab environment — not for production)
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $true

# Increase max envelope size for large Ansible payloads
Set-Item -Path WSMan:\localhost\MaxEnvelopeSizekb -Value 8192

# Ensure HTTP listener exists on all addresses
$httpListener = Get-ChildItem WSMan:\localhost\Listener |
    Where-Object { $_.Keys -contains "Transport=HTTP" }

if (-not $httpListener) {
    winrm create winrm/config/Listener?Address=*+Transport=HTTP
}

# Firewall rule
$rule = Get-NetFirewallRule -DisplayName "WinRM HTTP" -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName "WinRM HTTP" `
        -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow
}

Write-Host "=== WinRM ready ==="
