Write-Host "Installation des drivers VirtIO..."

# Trouver la lettre du lecteur VirtIO
$virtioCD = Get-WmiObject -Class Win32_CDROMDrive | Where-Object { $_.VolumeName -like "*virtio*" } | Select-Object -ExpandProperty Drive

if ($virtioCD) {
    Write-Host "ISO VirtIO trouvé sur $virtioCD"
    
    # Installer les drivers principaux
    $drivers = @(
        "Balloon\2k22\amd64",
        "NetKVM\2k22\amd64",
        "vioserial\2k22\amd64",
        "viostor\2k22\amd64",
        "vioscsi\2k22\amd64"
    )
    
    foreach ($driver in $drivers) {
        $driverPath = "$virtioCD\$driver"
        if (Test-Path $driverPath) {
            Write-Host "Installation de $driver..."
            pnputil.exe /add-driver "$driverPath\*.inf" /install /subdirs
        }
    }
    
    # Installer l'agent QEMU Guest Agent
    $qemuAgent = "$virtioCD\guest-agent\qemu-ga-x86_64.msi"
    if (Test-Path $qemuAgent) {
        Write-Host "Installation de QEMU Guest Agent..."
        Start-Process msiexec.exe -ArgumentList "/i `"$qemuAgent`" /qn /norestart" -Wait
    }
    
    Write-Host "Drivers VirtIO installés avec succès"
} else {
    Write-Host "ERREUR: ISO VirtIO non trouvé" -ForegroundColor Red
    # Chercher manuellement
    Get-WmiObject -Class Win32_CDROMDrive | ForEach-Object {
        Write-Host "CD trouvé: $($_.Drive) - $($_.VolumeName)"
    }
}

# Activer le service QEMU Guest Agent
Set-Service -Name "QEMU-GA" -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name "QEMU-GA" -ErrorAction SilentlyContinue

Write-Host "Installation VirtIO terminée"

