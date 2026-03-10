# Configuration WinRM pour Ansible
Write-Host "Configuration WinRM pour Ansible..."

# Activer WinRM
Enable-PSRemoting -Force

# Configuration du service WinRM
Set-Service -Name WinRM -StartupType Automatic
Start-Service -Name WinRM

# Autoriser l'authentification Basic (pour tests)
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true

# Autoriser les connexions non chiffrées (pour tests uniquement)
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $true

# Configurer le firewall
New-NetFirewallRule -DisplayName "WinRM HTTP" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow

# Créer un listener HTTP
winrm create winrm/config/Listener?Address=*+Transport=HTTP

Write-Host "WinRM configuré avec succès"

