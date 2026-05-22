# Debug : affiche les lecteurs disponibles
Write-Host 'Lecteurs disponibles :'
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root | Format-Table -AutoSize | Out-String | Write-Host

# Recherche du MSI sur tous les lecteurs possibles
$msi = Get-ChildItem -Path D:,E:,F:,G:,H:,I: -Filter 'CloudbaseInitSetup_*.msi' -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $msi) { throw 'CloudbaseInit MSI introuvable sur les lecteurs montés' }
Write-Host "MSI trouvé : $($msi.FullName)"

Copy-Item $msi.FullName 'C:\Temp\CloudbaseInitSetup.msi' -Force

# USERNAME=LocalSystem évite la création d'un compte local (erreur 1603)
Start-Process msiexec.exe -ArgumentList '/i C:\Temp\CloudbaseInitSetup.msi /qn /l*v C:\Temp\cbinit.log ADDLOCAL=CloudbaseInitService USERNAME=LocalSystem USERPASSWORD=' -Wait

# Vérification de l'installation
if (-not (Test-Path 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\conf')) {
    Get-Content 'C:\Temp\cbinit.log' -Tail 80 | Write-Host
    throw 'Cloudbase-Init installation failed'
}

# Copie des fichiers de conf
$confDir = 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\conf'
Copy-Item 'C:\Temp\cloudbase-init.conf'          "$confDir\cloudbase-init.conf"          -Force
Copy-Item 'C:\Temp\cloudbase-init-unattend.conf' "$confDir\cloudbase-init-unattend.conf" -Force

Set-Service -Name 'cloudbase-init' -StartupType Automatic