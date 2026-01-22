Write-Host "Installation de Cloudbase-Init..."

# Télécharger Cloudbase-Init
$url = "https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi"
$output = "C:\cloudbase-init.msi"

Invoke-WebRequest -Uri $url -OutFile $output

# Installer silencieusement
msiexec /i $output /qn /norestart

Write-Host "Cloudbase-Init installé"

