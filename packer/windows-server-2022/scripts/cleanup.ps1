Write-Host "=== Final cleanup ==="

# Clear event logs
Get-EventLog -LogName * | ForEach-Object { Clear-EventLog $_.Log }

# Remove temp files
# Exclude packer-* and script-* to avoid breaking subsequent Packer provisioners
Get-ChildItem "C:\Windows\Temp\*" -Exclude "packer-*","script-*" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Users\*\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Optimize disk (helps with template compression)
Optimize-Volume -DriveLetter C -Defrag -ErrorAction SilentlyContinue

Write-Host "=== Cleanup complete - sysprep will run via shutdown_command ==="
