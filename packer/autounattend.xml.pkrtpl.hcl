<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend"
          xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">

    <!-- ═══════════════════════════════════════════════════════════
         Pass 1 — windowsPE: language, disk, drivers
         ═══════════════════════════════════════════════════════════ -->
    <settings pass="windowsPE">
        <component name="Microsoft-Windows-International-Core-WinPE"
                   processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35"
                   language="neutral" versionScope="nonSxS">
            <SetupUILanguage>
                <UILanguage>en-US</UILanguage>
            </SetupUILanguage>
            <InputLocale>fr-FR</InputLocale>
            <SystemLocale>en-US</SystemLocale>
            <UILanguage>en-US</UILanguage>
            <UserLocale>en-US</UserLocale>
        </component>

        <component name="Microsoft-Windows-Setup"
                   processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35"
                   language="neutral" versionScope="nonSxS">

            <!-- GPT partitioning for UEFI -->
            <DiskConfiguration>
                <Disk wcm:action="add">
                    <DiskID>0</DiskID>
                    <WillWipeDisk>true</WillWipeDisk>
                    <CreatePartitions>
                        <CreatePartition wcm:action="add">
                            <Order>1</Order>
                            <Type>EFI</Type>
                            <Size>100</Size>
                        </CreatePartition>
                        <CreatePartition wcm:action="add">
                            <Order>2</Order>
                            <Type>MSR</Type>
                            <Size>128</Size>
                        </CreatePartition>
                        <CreatePartition wcm:action="add">
                            <Order>3</Order>
                            <Type>Primary</Type>
                            <Extend>true</Extend>
                        </CreatePartition>
                    </CreatePartitions>
                    <ModifyPartitions>
                        <ModifyPartition wcm:action="add">
                            <Order>1</Order>
                            <PartitionID>1</PartitionID>
                            <Label>System</Label>
                            <Format>FAT32</Format>
                        </ModifyPartition>
                        <ModifyPartition wcm:action="add">
                            <Order>2</Order>
                            <PartitionID>2</PartitionID>
                        </ModifyPartition>
                        <ModifyPartition wcm:action="add">
                            <Order>3</Order>
                            <PartitionID>3</PartitionID>
                            <Label>Windows</Label>
                            <Format>NTFS</Format>
                            <Letter>C</Letter>
                        </ModifyPartition>
                    </ModifyPartitions>
                </Disk>
            </DiskConfiguration>

            <!-- Windows Server 2022 Standard (Desktop Experience) = index 2 -->
            <ImageInstall>
                <OSImage>
                    <InstallFrom>
                        <MetaData wcm:action="add">
                            <Key>/IMAGE/INDEX</Key>
                            <Value>2</Value>
                        </MetaData>
                    </InstallFrom>
                    <InstallTo>
                        <DiskID>0</DiskID>
                        <PartitionID>3</PartitionID>
                    </InstallTo>
                </OSImage>
            </ImageInstall>

            <UserData>
                <AcceptEula>true</AcceptEula>
                <FullName>Administrator</FullName>
                <Organization>Lab</Organization>
            </UserData>

            <!-- VirtIO drivers — try D: E: F: (drive letter varies by CD slot) -->
            <DriverPaths>
                <PathAndCredentials wcm:action="add" wcm:keyValue="1">
                    <Path>D:\vioscsi\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="2">
                    <Path>D:\viostor\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="3">
                    <Path>D:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="4">
                    <Path>E:\vioscsi\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="5">
                    <Path>E:\viostor\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="6">
                    <Path>E:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="7">
                    <Path>F:\vioscsi\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="8">
                    <Path>F:\viostor\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="9">
                    <Path>F:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
            </DriverPaths>
        </component>
    </settings>

    <!-- ═══════════════════════════════════════════════════════════
         Pass 2 — specialize: hostname, timezone
         ═══════════════════════════════════════════════════════════ -->
    <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup"
                   processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35"
                   language="neutral" versionScope="nonSxS">
            <ComputerName>WIN-TEMPLATE</ComputerName>
            <TimeZone>Romance Standard Time</TimeZone>
        </component>
    </settings>

    <!-- ═══════════════════════════════════════════════════════════
         Pass 3 — oobeSystem: admin account, auto-logon, WinRM bootstrap
         ═══════════════════════════════════════════════════════════ -->
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup"
                   processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35"
                   language="neutral" versionScope="nonSxS">

            <AutoLogon>
                <Password>
                    <Value>${admin_password}</Value>
                    <PlainText>true</PlainText>
                </Password>
                <Enabled>true</Enabled>
                <Username>Administrator</Username>
            </AutoLogon>

            <UserAccounts>
                <AdministratorPassword>
                    <Value>${admin_password}</Value>
                    <PlainText>true</PlainText>
                </AdministratorPassword>
            </UserAccounts>

            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
                <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
                <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
                <ProtectYourPC>3</ProtectYourPC>
            </OOBE>

            <FirstLogonCommands>
                <!-- 1. Set static IP so Packer can reach the VM -->
                <SynchronousCommand wcm:action="add">
                    <Order>1</Order>
                    <Description>Set static IP</Description>
                    <CommandLine>cmd /c netsh interface ip set address "Ethernet" static ${vm_ip} ${vm_netmask} ${vm_gateway}</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>2</Order>
                    <Description>Set DNS</Description>
                    <CommandLine>cmd /c netsh interface ip set dns "Ethernet" static ${vm_dns}</CommandLine>
                </SynchronousCommand>

                <!-- 2. Set execution policy -->
                <SynchronousCommand wcm:action="add">
                    <Order>3</Order>
                    <Description>Set Execution Policy</Description>
                    <CommandLine>powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force"</CommandLine>
                </SynchronousCommand>

                <!-- 3. Bootstrap WinRM so Packer can connect -->
                <SynchronousCommand wcm:action="add">
                    <Order>4</Order>
                    <Description>Enable WinRM</Description>
                    <CommandLine>cmd /c winrm quickconfig -quiet</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>5</Order>
                    <Description>Configure WinRM for Packer</Description>
                    <CommandLine>powershell -Command "Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true; Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true; Set-Item WSMan:\localhost\MaxTimeoutms -Value 1800000; Restart-Service WinRM"</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>6</Order>
                    <Description>Open Firewall for WinRM</Description>
                    <CommandLine>powershell -Command "New-NetFirewallRule -DisplayName 'WinRM HTTP' -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue"</CommandLine>
                </SynchronousCommand>
            </FirstLogonCommands>
        </component>

        <!-- Keep AZERTY keyboard in OOBE -->
        <component name="Microsoft-Windows-International-Core"
                   processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35"
                   language="neutral" versionScope="nonSxS">
            <InputLocale>fr-FR</InputLocale>
            <SystemLocale>en-US</SystemLocale>
            <UILanguage>en-US</UILanguage>
            <UserLocale>en-US</UserLocale>
        </component>
    </settings>
</unattend>
