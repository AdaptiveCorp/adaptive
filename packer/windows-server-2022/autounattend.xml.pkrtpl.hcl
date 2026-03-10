<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend"
          xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">

    <settings pass="windowsPE">
        <component name="Microsoft-Windows-PnpCustomizationsWinPE" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" processorArchitecture="amd64">
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
                    <Path>D:\Balloon\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="5">
                    <Path>D:\pvpanic\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="6">
                    <Path>D:\qemupciserial\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="7">
                    <Path>D:\vioinput\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="8">
                    <Path>D:\viorng\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="9">
                    <Path>D:\vioserial\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="10">
                    <Path>E:\vioscsi\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="11">
                    <Path>E:\viostor\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="12">
                    <Path>E:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="13">
                    <Path>E:\Balloon\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="14">
                    <Path>E:\pvpanic\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="15">
                    <Path>E:\qemupciserial\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="16">
                    <Path>E:\vioinput\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="17">
                    <Path>E:\viorng\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="18">
                    <Path>E:\vioserial\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="19">
                    <Path>F:\vioscsi\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="20">
                    <Path>F:\viostor\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="21">
                    <Path>F:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
                <PathAndCredentials wcm:action="add" wcm:keyValue="22">
                    <Path>F:\NetKVM\2k22\amd64</Path>
                </PathAndCredentials>
            </DriverPaths>
        </component>
        <component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <SetupUILanguage>
                <UILanguage>en-US</UILanguage>
            </SetupUILanguage>
            <InputLocale>fr-FR</InputLocale>
            <SystemLocale>en-US</SystemLocale>
            <UILanguage>en-US</UILanguage>
            <UserLocale>en-US</UserLocale>
        </component>
        <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
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
                            <Label>Windows 2022</Label>
                            <Format>NTFS</Format>
                            <Letter>C</Letter>
                        </ModifyPartition>
                    </ModifyPartitions>
                </Disk>
                <WillShowUI>OnError</WillShowUI>
            </DiskConfiguration>
            <UserData>
                <AcceptEula>true</AcceptEula>
                <FullName>Administrator</FullName>
                <Organization>ADaptive</Organization>
                <ProductKey>
                    <WillShowUI>OnError</WillShowUI>
                </ProductKey>
            </UserData>
            <ImageInstall>
                <OSImage>
                    <InstallTo>
                        <DiskID>0</DiskID>
                        <PartitionID>3</PartitionID>
                    </InstallTo>
                    <WillShowUI>OnError</WillShowUI>
                    <InstallToAvailablePartition>false</InstallToAvailablePartition>
                    <InstallFrom>
                        <MetaData wcm:action="add">
                            <Key>/IMAGE/NAME</Key>
                            <Value>Windows Server 2022 SERVERSTANDARD</Value>
                        </MetaData>
                    </InstallFrom>
                </OSImage>
            </ImageInstall>
        </component>
    </settings>

    <settings pass="specialize">
        <component name="Microsoft-Windows-ServerManager-SvrMgrNc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <DoNotOpenServerManagerAtLogon>true</DoNotOpenServerManagerAtLogon>
        </component>
        <component name="Microsoft-Windows-IE-ESC" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <IEHardenAdmin>false</IEHardenAdmin>
            <IEHardenUser>false</IEHardenUser>
        </component>
        <component name="Microsoft-Windows-OutOfBoxExperience" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <DoNotOpenInitialConfigurationTasksAtLogon>true</DoNotOpenInitialConfigurationTasksAtLogon>
        </component>
        <component name="Microsoft-Windows-Security-SPP-UX" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <SkipAutoActivation>true</SkipAutoActivation>
        </component>
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <ComputerName>WIN-TEMPLATE</ComputerName>
            <TimeZone>Romance Standard Time</TimeZone>
        </component>
        <component name="Microsoft-Windows-TerminalServices-LocalSessionManager" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <fDenyTSConnections>false</fDenyTSConnections>
        </component>
        <component name="Networking-MPSSVC-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <FirewallGroups>
                <FirewallGroup wcm:action="add" wcm:keyValue="RemoteDesktop">
                    <Active>true</Active>
                    <Group>Remote Desktop</Group>
                    <Profile>all</Profile>
                </FirewallGroup>
            </FirewallGroups>
        </component>
        <component name="Microsoft-Windows-TerminalServices-RDP-WinStationExtensions" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <UserAuthentication>0</UserAuthentication>
        </component>
        <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <InputLocale>fr-FR</InputLocale>
            <SystemLocale>en-US</SystemLocale>
            <UILanguage>en-US</UILanguage>
            <UserLocale>en-US</UserLocale>
        </component>
    </settings>

    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <AutoLogon>
                <Enabled>true</Enabled>
                <Username>Administrator</Username>
                <Password>
                    <Value>${admin_password}</Value>
                    <PlainText>true</PlainText>
                </Password>
            </AutoLogon>
            <FirstLogonCommands>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>reg add HKLM\System\CurrentControlSet\Control\Network\NewNetworkWindowOff</CommandLine>
                    <Order>1</Order>
                    <RequiresUserInput>true</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>2</Order>
                    <CommandLine>cmd /c netsh interface ip set address "Ethernet" static ${vm_ip} ${vm_netmask} ${vm_gateway}</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>3</Order>
                    <CommandLine>cmd /c netsh interface ip set dns "Ethernet" static ${vm_dns}</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>4</Order>
                    <CommandLine>cmd /c "if exist D:\setup-for-ansible.ps1 (powershell -NoProfile -ExecutionPolicy Bypass D:\setup-for-ansible.ps1) else if exist E:\setup-for-ansible.ps1 (powershell -NoProfile -ExecutionPolicy Bypass E:\setup-for-ansible.ps1) else if exist F:\setup-for-ansible.ps1 (powershell -NoProfile -ExecutionPolicy Bypass F:\setup-for-ansible.ps1) else if exist G:\setup-for-ansible.ps1 (powershell -NoProfile -ExecutionPolicy Bypass G:\setup-for-ansible.ps1)"</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>5</Order>
                    <CommandLine>cmd /c "if exist D:\windows-common-setup.ps1 (powershell -NoProfile -ExecutionPolicy Bypass D:\windows-common-setup.ps1) else if exist E:\windows-common-setup.ps1 (powershell -NoProfile -ExecutionPolicy Bypass E:\windows-common-setup.ps1) else if exist F:\windows-common-setup.ps1 (powershell -NoProfile -ExecutionPolicy Bypass F:\windows-common-setup.ps1) else if exist G:\windows-common-setup.ps1 (powershell -NoProfile -ExecutionPolicy Bypass G:\windows-common-setup.ps1)"</CommandLine>
                </SynchronousCommand>
            </FirstLogonCommands>
            <OOBE>
                <HideLocalAccountScreen>true</HideLocalAccountScreen>
                <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
                <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
                <NetworkLocation>Work</NetworkLocation>
                <ProtectYourPC>3</ProtectYourPC>
                <HideEULAPage>true</HideEULAPage>
                <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
            </OOBE>
            <UserAccounts>
                <AdministratorPassword>
                    <Value>${admin_password}</Value>
                    <PlainText>true</PlainText>
                </AdministratorPassword>
            </UserAccounts>
            <TimeZone>Romance Standard Time</TimeZone>
        </component>
        <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <InputLocale>fr-FR</InputLocale>
            <SystemLocale>en-US</SystemLocale>
            <UILanguage>en-US</UILanguage>
            <UserLocale>en-US</UserLocale>
        </component>
    </settings>

    <settings pass="offlineServicing">
        <component name="Microsoft-Windows-LUA-Settings" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <EnableLUA>false</EnableLUA>
        </component>
    </settings>
</unattend>
