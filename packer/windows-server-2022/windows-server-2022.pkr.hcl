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
    type     = "ide"
    index    = 0
    iso_file = var.virtio_iso_file
    unmount  = true
  }

  additional_iso_files {
    type     = "ide"
    index    = 1
    iso_file = "local:iso/CloudbaseInitSetup_1_1_8_x64.iso"
    unmount  = true
  }

  additional_iso_files {
    type     = "sata"
    index    = 0
    cd_label = "Unattend"
    cd_content = {
      "autounattend.xml" = templatefile("${path.root}/iso/autounattend.xml.pkrtpl", {
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
  winrm_host     = "10.0.0.50"
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
    script            = "${path.root}/scripts/install-virtio.ps1"
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    script            = "${path.root}/scripts/init-dirs.ps1"
  }

  provisioner "file" {
    source      = "${path.root}/files/cloudbase-init.conf"
    destination = "C:\\Temp\\cloudbase-init.conf"
  }

  provisioner "file" {
    source      = "${path.root}/files/cloudbase-init-unattend.conf"
    destination = "C:\\Temp\\cloudbase-init-unattend.conf"
  }

  provisioner "file" {
    source      = "${path.root}/files/ping-url.ps1"
    destination = "C:\\Scripts\\ping-url.ps1"
  }

  provisioner "windows-restart" {
    restart_timeout = "15m"
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    script            = "${path.root}/scripts/install-cloudbase.ps1"
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    script            = "${path.root}/scripts/register-ping-url-task.ps1"
  }

  provisioner "powershell" {
    elevated_user     = var.winrm_username
    elevated_password = var.winrm_password
    script            = "${path.root}/scripts/sysprep.ps1"
    valid_exit_codes  = [0, 1]
  }
}