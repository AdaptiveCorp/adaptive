$ErrorActionPreference = "Continue"

if (-not (Test-Path "C:\adaptive")) {
    New-Item -ItemType Directory -Path "C:\adaptive"
}
Start-Transcript -path C:\adaptive\setup-log.txt -append

Start-Service -Name 'WinRM' -ErrorAction Stop

$VirtioDrive = $null
foreach ($d in @('D','E','F','G')) {
    if (Test-Path "$d`:\guest-agent\qemu-ga-x86_64.msi") {
        $VirtioDrive = $d
        break
    }
}

if ($VirtioDrive) {
    if ([System.Environment]::Is64BitOperatingSystem) {
        & "$VirtioDrive`:\guest-agent\qemu-ga-x86_64.msi" /quiet
    }
    else {
        & "$VirtioDrive`:\guest-agent\qemu-ga-x86.msi" /quiet
    }
}

Get-NetAdapter | foreach { Disable-NetAdapterBinding -InterfaceAlias $_.Name -ComponentID ms_tcpip6 }

netsh advfirewall firewall add rule name='ICMP Allow incoming V4 echo request' protocol=icmpv4:8,any dir=in action=allow

netsh interface teredo set state disabled

wmic useraccount where "name='Administrator'" set PasswordExpires=FALSE

New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "IPAutoconfigurationEnabled" -Value 0 -PropertyType DWORD -Force
