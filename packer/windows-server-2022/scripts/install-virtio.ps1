$driverPath = 'E:\vioscsi\w10\amd64'
if (Test-Path $driverPath) { pnputil /add-driver "$driverPath\vioscsi.inf" /install }

$netPath = 'E:\NetKVM\2k22\amd64'
if (Test-Path $netPath) { pnputil /add-driver "$netPath\netkvm.inf" /install }
elseif (Test-Path 'E:\NetKVM\w10\amd64') { pnputil /add-driver 'E:\NetKVM\w10\amd64\netkvm.inf' /install }

$balloonPath = 'E:\Balloon\2k22\amd64'
if (Test-Path $balloonPath) { pnputil /add-driver "$balloonPath\balloon.inf" /install }

$qemuGa = 'E:\guest-agent\qemu-ga-x86_64.msi'
if (Test-Path $qemuGa) { Start-Process msiexec.exe -ArgumentList "/i `"$qemuGa`" /qn /norestart" -Wait }