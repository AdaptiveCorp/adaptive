packer {
  required_plugins {
    proxmox = {
      version = "v1.2.3"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "windows-server" {
  # Connexion Proxmox
  proxmox_url              = var.proxmox_api_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true
  node                     = var.proxmox_node

  # Configuration VM
  vm_name              = var.vm_name
  template_description = "Windows Server 2022 - WinRM + Cloudbase-Init"
  memory               = var.memory
  cores                = var.cpus
  cpu_type             = "host"
  os                   = "win11"
  bios                 = "ovmf"
  machine              = "q35"
  
  # EFI Configuration
  efi_config {
    efi_storage_pool  = var.storage_pool
    pre_enrolled_keys = true
    efi_type          = "4m"
  }

  # ISO Configuration Windows
  boot_iso {
    iso_file    = var.iso_file
    unmount     = true
    type        = "sata"
  }
  
  # ISO VirtIO drivers
  additional_iso_files {
    device   = "ide3"
    iso_file = var.virtio_iso
    unmount  = true
    type     = "ide"
  }


  # Disque
  disks {
    storage_pool = var.storage_pool
    type         = "scsi"
    disk_size    = var.disk_size
    format       = "raw"
    cache_mode   = "writeback"
  }
  
  scsi_controller = "virtio-scsi-pci"
  
  http_directory = "http"
  http_port_min  = 8802
  http_port_max  = 8802
 
  # Réseau
  network_adapters {
    model  = "virtio"
    bridge = "vmbr0"
  }

  # Agent QEMU
  qemu_agent = true

  # Communication WinRM
  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_password = var.admin_password
  winrm_timeout  = "12h"
  winrm_use_ssl  = false
  winrm_insecure = true

  # Boot
  boot_wait = "3s"
  boot_command = ["<spacebar>"]
}


build {
  name    = "windows-server-2022-build"
  sources = ["source.proxmox-iso.windows-server"]

  # 1. Installation VirtIO drivers
  provisioner "powershell" {
    scripts = ["./scripts/install-virtio.ps1"]
  }

  # 2. Configuration WinRM pour Ansible
  provisioner "powershell" {
    scripts = ["./scripts/setup-winrm.ps1"]
  }

  # 3. Installation Cloudbase-Init
  provisioner "powershell" {
    scripts = ["./scripts/install-cloudbase.ps1"]
  }

  # 4. Windows Updates (optionnel mais recommandé)
  # provisioner "windows-update" {
  #    search_criteria = "IsInstalled=0"
  #    filters = [
  #      "exclude:$_.Title -like '*Preview*'",
  #      "include:$true"
  #    ]
  #    update_limit = 50
  #   }

  # 5. Nettoyage final
  provisioner "powershell" {
    scripts = ["./scripts/cleanup.ps1"]
  }
}

