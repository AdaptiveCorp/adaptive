# ── WinRM configuration for Ansible ──────────────────────────
# Sets up HTTP + HTTPS listeners, CredSSP auth, and firewall rules.
# Reference: https://docs.ansible.com/ansible/latest/os_guide/windows_winrm.html

Write-Host "=== Configuring WinRM for Ansible ==="

# ── Enable PSRemoting ────────────────────────────────────────
Enable-PSRemoting -Force

# ── Service settings ─────────────────────────────────────────
Set-Service -Name WinRM -StartupType Automatic

# Increase shell limits for Ansible (large playbooks / long tasks)
Set-Item -Path WSMan:\localhost\Shell\MaxMemoryPerShellMB -Value 1024
Set-Item -Path WSMan:\localhost\Shell\MaxConcurrentUsers -Value 10
Set-Item -Path WSMan:\localhost\MaxTimeoutms -Value 1800000

# ── Authentication methods ───────────────────────────────────
# Basic   — needed for simple username/password over HTTP (lab only)
# CredSSP — needed for AD operations (domain join, DC promo, etc.)
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\CredSSP -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\Negotiate -Value $true

# Allow unencrypted for HTTP (lab environment)
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $true

# ── HTTP listener (port 5985) ────────────────────────────────
# Already created by Enable-PSRemoting, ensure it exists
$httpListener = Get-WSManInstance -ResourceURI winrm/config/Listener -Enumerate |
    Where-Object { $_.Transport -eq "HTTP" }

if (-not $httpListener) {
    New-WSManInstance -ResourceURI winrm/config/Listener `
        -SelectorSet @{Address="*"; Transport="HTTP"}
    Write-Host "HTTP listener created on port 5985"
}

# ── HTTPS listener (port 5986) ───────────────────────────────
# Self-signed certificate — sufficient for lab/pentest environments
$cert = New-SelfSignedCertificate `
    -CertStoreLocation Cert:\LocalMachine\My `
    -DnsName $env:COMPUTERNAME, "localhost" `
    -NotAfter (Get-Date).AddYears(10) `
    -Subject "CN=$env:COMPUTERNAME"

# Remove existing HTTPS listener if any
$existing = Get-WSManInstance -ResourceURI winrm/config/Listener -Enumerate |
    Where-Object { $_.Transport -eq "HTTPS" }

if ($existing) {
    Remove-WSManInstance -ResourceURI winrm/config/Listener `
        -SelectorSet @{Address="*"; Transport="HTTPS"}
}

New-WSManInstance -ResourceURI winrm/config/Listener `
    -SelectorSet @{Address="*"; Transport="HTTPS"} `
    -ValueSet @{CertificateThumbprint=$cert.Thumbprint; Port="5986"}

Write-Host "HTTPS listener created on port 5986 (thumbprint: $($cert.Thumbprint))"

# ── Enable CredSSP ───────────────────────────────────────────
Enable-WSManCredSSP -Role Server -Force

# ── LocalAccountTokenFilterPolicy ────────────────────────────
# Required for WinRM with local admin accounts
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" `
    -Name "LocalAccountTokenFilterPolicy" `
    -Value 1 -PropertyType DWORD -Force | Out-Null

# ── Firewall rules ───────────────────────────────────────────
New-NetFirewallRule -DisplayName "WinRM HTTP (5985)" `
    -Direction Inbound -LocalPort 5985 -Protocol TCP `
    -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null

New-NetFirewallRule -DisplayName "WinRM HTTPS (5986)" `
    -Direction Inbound -LocalPort 5986 -Protocol TCP `
    -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null

# ── Restart service ──────────────────────────────────────────
Restart-Service WinRM

Write-Host "=== WinRM configuration complete ==="
Write-Host "  HTTP  : port 5985 (Basic, Negotiate, CredSSP)"
Write-Host "  HTTPS : port 5986 (self-signed cert)"
