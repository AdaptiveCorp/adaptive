Write-Host "Nettoyage du système..."

# Vider les logs
Get-EventLog -LogName * | ForEach-Object { Clear-EventLog $_.Log }

# Nettoyer les fichiers temporaires
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Users\*\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Défragmenter et optimiser le disque
Optimize-Volume -DriveLetter C -Defrag

Write-Host "Nettoyage terminé"

