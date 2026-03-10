packer {
  required_plugins {
    proxmox = {
      version = "~> 1.2.2"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

locals {
  template_description = "Windows Server 2022 — ADaptive (built ${legacy_isotime("2006-01-02 15:04:05")})"
}

source "proxmox-iso" "windows-server" {
  proxmox_url              = var.proxmox_api_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true
  node                     = var.proxmox_node

  vm_name              = var.vm_name
  template_description = local.template_description
  memory               = var.memory
  cores                = var.cpus
  cpu_type             = "host"
  os                   = "win11"
  bios                 = "ovmf"
  machine              = "q35"
  qemu_agent           = true

  efi_config {
    efi_storage_pool  = var.storage_pool
    pre_enrolled_keys = true
    efi_type          = "4m"
  }

  disks {
    storage_pool = var.storage_pool
    type         = "scsi"
    disk_size    = var.disk_size
    format       = "raw"
    cache_mode   = "writeback"
    ssd          = true
    discard      = true
    io_thread    = true
  }

  scsi_controller = "virtio-scsi-single"

  network_adapters {
    model  = "virtio"
    bridge = var.network_bridge
  }

  boot_iso {
    iso_file = var.iso_file
    unmount  = true
    type     = "sata"
  }

  additional_iso_files {
    type     = "sata"
    index    = 1
    iso_file = var.virtio_iso
    unmount  = true
  }

  additional_iso_files {
    type             = "sata"
    index            = 2
    unmount          = true
    cd_label         = "PROVISION"
    iso_storage_pool = var.iso_storage_pool
    cd_content = {
      "autounattend.xml" = templatefile("${path.root}/autounattend.xml.pkrtpl.hcl", {
        admin_password = var.admin_password
        vm_ip          = var.vm_ip
        vm_gateway     = var.vm_gateway
        vm_netmask     = var.vm_netmask
        vm_dns         = var.vm_dns
      })
    }
    cd_files = [
      "${path.root}/../scripts/setup-for-ansible.ps1",
      "${path.root}/../scripts/windows-common-setup.ps1",
    ]
  }

  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_password = var.admin_password
  winrm_insecure = true
  winrm_use_ssl  = true
  winrm_timeout  = "6h"

  boot      = "order=sata0;scsi0"
  boot_wait = "5s"
  boot_command = [
    "<spacebar><spacebar><spacebar>"
  ]

  cloud_init              = true
  cloud_init_storage_pool = var.storage_pool

  task_timeout = "20m"
}


build {
  name    = "windows-server-2022"
  sources = ["source.proxmox-iso.windows-server"]

  provisioner "windows-shell" {
    scripts = ["${path.root}/../scripts/disable-winupdate.bat"]
  }

  provisioner "powershell" {
    scripts = ["${path.root}/../scripts/disable-hibernate.ps1"]
  }

  provisioner "powershell" {
    scripts = ["${path.root}/../scripts/install-virtio-drivers.ps1"]
  }

  provisioner "powershell" {
    scripts = ["${path.root}/../scripts/install-cloudbase.ps1"]
  }

  provisioner "powershell" {
    scripts = ["${path.root}/../scripts/cleanup.ps1"]
  }
}
