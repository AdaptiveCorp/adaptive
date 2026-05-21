packer {
  required_plugins {
    proxmox = {
      version = ">= 1.1.8"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "windows-server-2022" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = var.proxmox_skip_tls_verify
  node                     = var.proxmox_node

  vm_id                = var.vm_id
  vm_name              = var.vm_name
  template_name        = var.vm_name
  template_description = var.template_description

  os   = "win11"
  bios = "seabios"

  boot_iso {
    type     = "ide"
    index    = 2
    iso_file = var.iso_file
    unmount  = true
  }

  additional_iso_files {
    type             = "ide"
    index            = 0
    iso_file         = var.virtio_iso_file
    unmount          = true
  }

  additional_iso_files {
    type     = "sata"
    index    = 0
    cd_label = "Unattend"
    cd_content = {
      "autounattend.xml" = templatefile("${path.root}/http/autounattend.xml.pkrtpl", {
        winrm_password = var.winrm_password
      })
    }
    iso_storage_pool = var.iso_storage_pool
    unmount          = true
  }

  boot      = "order=ide2;scsi0;net0"
  boot_wait = "5s"
  boot_command = []

  cores   = var.vm_cpu_cores
  sockets = var.vm_cpu_sockets
  memory  = var.vm_memory

  disks {
    type         = "scsi"
    disk_size    = var.vm_disk_size
    storage_pool = var.proxmox_storage
    format       = "raw"
    cache_mode   = "writeback"
    discard      = true
    io_thread    = true
  }

  scsi_controller = "virtio-scsi-single"

  network_adapters {
    model    = "virtio"
    bridge   = var.network_bridge
    firewall = false
  }

  cloud_init              = true
  cloud_init_storage_pool = var.proxmox_storage

  qemu_agent = true

  communicator   = "winrm"
  winrm_username = var.winrm_username
  winrm_password = var.winrm_password
  winrm_use_ssl  = false
  winrm_insecure = true
  winrm_no_proxy = true
  winrm_timeout  = "90m"
}

build {
  name    = "windows-server-2022"
  sources = ["source.proxmox-iso.windows-server-2022"]

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    inline = [
      "$driverPath = 'E:\\vioscsi\\w10\\amd64'",
      "if (Test-Path $driverPath) { pnputil /add-driver \"$driverPath\\vioscsi.inf\" /install }",
      "$netPath = 'E:\\NetKVM\\2k22\\amd64'",
      "if (Test-Path $netPath) { pnputil /add-driver \"$netPath\\netkvm.inf\" /install }",
      "elseif (Test-Path 'E:\\NetKVM\\w10\\amd64') { pnputil /add-driver 'E:\\NetKVM\\w10\\amd64\\netkvm.inf' /install }",
      "$balloonPath = 'E:\\Balloon\\2k22\\amd64'",
      "if (Test-Path $balloonPath) { pnputil /add-driver \"$balloonPath\\balloon.inf\" /install }",
      "$qemuGa = 'E:\\guest-agent\\qemu-ga-x86_64.msi'",
      "if (Test-Path $qemuGa) { Start-Process msiexec.exe -ArgumentList \"/i `\"$qemuGa`\" /qn /norestart\" -Wait }"
    ]
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    inline = [
      "New-Item -ItemType Directory -Force -Path 'C:\\Scripts' | Out-Null",
      "New-Item -ItemType Directory -Force -Path 'C:\\Temp'    | Out-Null"
    ]
  }

  provisioner "file" {
    source      = "${path.root}/files/CloudbaseInitSetup_1_1_8_x64.msi"
    destination = "C:\\Temp\\CloudbaseInitSetup_1_1_8_x64.msi"
  }

  provisioner "file" {
    source      = "${path.root}/config/cloudbase-init.conf"
    destination = "C:\\Temp\\cloudbase-init.conf"
  }

  provisioner "file" {
    source      = "${path.root}/config/cloudbase-init-unattend.conf"
    destination = "C:\\Temp\\cloudbase-init-unattend.conf"
  }

  provisioner "file" {
    source      = "${path.root}/scripts/ping-url.ps1"
    destination = "C:\\Scripts\\ping-url.ps1"
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    inline = [
      "Start-Process msiexec.exe -ArgumentList \"/i C:\\Temp\\CloudbaseInitSetup_1_1_8_x64.msi /qn /l*v C:\\Temp\\cbinit.log ADDLOCAL=CloudbaseInitService\" -Wait",
      "$confDir = 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf'",
      "Copy-Item 'C:\\Temp\\cloudbase-init.conf'          \"$confDir\\cloudbase-init.conf\"          -Force",
      "Copy-Item 'C:\\Temp\\cloudbase-init-unattend.conf' \"$confDir\\cloudbase-init-unattend.conf\" -Force",
      "Set-Service -Name 'cloudbase-init' -StartupType Automatic"
    ]
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    inline = [
      "$action    = New-ScheduledTaskAction -Execute 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe' -Argument '-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File \"C:\\Scripts\\ping-url.ps1\"'",
      "$trigger   = New-ScheduledTaskTrigger -AtStartup",
      "$settings  = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)",
      "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest",
      "Register-ScheduledTask -TaskName 'ping-url' -TaskPath '\\' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null"
    ]
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    inline = [
      "$unattend = 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf\\Unattend.xml'",
      "& C:\\Windows\\System32\\Sysprep\\Sysprep.exe /generalize /oobe /shutdown \"/unattend:$unattend\""
    ]
    valid_exit_codes = [0, 1]
  }
}