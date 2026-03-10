<!-- :
@setlocal EnableDelayedExpansion EnableExtensions
@for %%i in (%~dp0\_packer_config*.cmd) do @call "%%~i"
@if defined PACKER_DEBUG (@echo on) else (@echo off)

echo ==^> Disabling Windows Updates

SC stop wuauserv
SC config wuauserv start= disabled

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions /t REG_DWORD /d 2 /f

reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate" /v DisableWindowsUpdateAccess /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f

schtasks.exe /change /tn "\Microsoft\Windows\UpdateOrchestrator\USO_UxBroker_Display" /disable >nul 2>&1
schtasks.exe /change /tn "\Microsoft\Windows\UpdateOrchestrator\MusUx_UpdateInterval" /disable >nul 2>&1
schtasks.exe /change /tn "\Microsoft\Windows\WindowsUpdate\sih" /disable >nul 2>&1

exit /b
