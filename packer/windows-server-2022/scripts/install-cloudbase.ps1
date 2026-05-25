$drives = @('D:','E:','F:','G:','H:','I:')
$msi = Get-ChildItem -Path $drives -Filter 'CloudbaseInitSetup_*.msi' -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $msi) { throw 'CloudbaseInit MSI introuvable sur les lecteurs montés' }
Write-Host "MSI trouvé : $($msi.FullName)"
Copy-Item $msi.FullName 'C:\Temp\CloudbaseInitSetup.msi' -Force

$proc = Start-Process msiexec.exe `
    -ArgumentList '/i C:\Temp\CloudbaseInitSetup.msi /qn /norestart /l*v C:\Temp\cbinit.log ADDLOCAL=CloudbaseInit USERNAME=LocalSystem USERPASSWORD=' `
    -Wait -PassThru

if ($proc.ExitCode -ne 0) {
    Get-Content 'C:\Temp\cbinit.log' -Tail 80 | Write-Host
    throw "Cloudbase-Init installation failed (exit code $($proc.ExitCode))"
}

$confDir = 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\conf'
Copy-Item 'C:\Temp\cloudbase-init.conf' "$confDir\cloudbase-init.conf" -Force
Copy-Item 'C:\Temp\cloudbase-init-unattend.conf' "$confDir\cloudbase-init-unattend.conf" -Force
Set-Service -Name 'cloudbase-init' -StartupType Automatic