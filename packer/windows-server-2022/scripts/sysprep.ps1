$unattend = "C:\Windows\System32\Sysprep\unattend.xml"
Start-Process -FilePath "C:\Windows\System32\Sysprep\sysprep.exe" `
    -ArgumentList "/generalize /oobe /shutdown /quiet /unattend:$unattend" `
    -Wait