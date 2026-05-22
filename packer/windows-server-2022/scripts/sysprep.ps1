$unattend = 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\conf\Unattend.xml'
& C:\Windows\System32\Sysprep\Sysprep.exe /generalize /oobe /shutdown "/unattend:$unattend"