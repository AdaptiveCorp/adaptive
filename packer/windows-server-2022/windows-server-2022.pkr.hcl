packer {
  required_plugins {
    proxmox = {
      version = ">= 1.2.2"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "windows-server" {
  # Proxmox connection
  proxmox_url              = var.proxmox_api_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true
  node                     = var.proxmox_node

  # VM settings
  vm_name              = var.vm_name
  template_description = "Windows Server 2022 — VirtIO + WinRM + Cloudbase-Init"
  memory               = var.memory
  cores                = var.cpus
  cpu_type             = "host"
  os                   = "win11"
  bios                 = "ovmf"
  machine              = "q35"
  qemu_agent           = true
  scsi_controller      = "virtio-scsi-pci"

  # Cloud-init drive for Proxmox (Cloudbase-Init reads it via NoCloud datasource)
  cloud_init              = true
  cloud_init_storage_pool = var.storage_pool

  # EFI
  efi_config {
    efi_storage_pool  = var.storage_pool
    pre_enrolled_keys = true
    efi_type          = "4m"
  }

  # Disk
  disks {
    storage_pool = var.storage_pool
    type         = "scsi"
    disk_size    = var.disk_size
    format       = "raw"
    cache_mode   = "writeback"
  }

  # Network (virtio for performance)
  network_adapters {
    model  = "virtio"
    bridge = "vmbr0"
  }

  # Windows Server ISO (boot drive)
  boot_iso {
    iso_file = var.iso_file
    unmount  = true
    type     = "sata"
  }

  # Autounattend.xml (templated with build IP + admin password)
  additional_iso_files {
    cd_content = {
      "autounattend.xml" = templatefile("./http/autounattend.xml.pkrtpl", {
        admin_password = var.admin_password
        build_ip       = var.build_ip
        build_netmask  = var.build_netmask
        build_gateway  = var.build_gateway
        build_dns      = var.build_dns
      })
    }
    cd_files         = ["./files/CloudbaseInitSetup_1_1_6_x64.msi"]
    cd_label         = "OEMDRV"
    iso_storage_pool = var.iso_storage_pool
    type             = "sata"
    index            = 1
    unmount          = true
  }

  # VirtIO drivers ISO
  additional_iso_files {
    iso_file = var.virtio_iso
    type     = "ide"
    index    = 3
    unmount  = true
  }

  # WinRM communicator (Packer <-> Windows)
  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_password = var.admin_password
  winrm_host     = var.build_ip
  winrm_timeout  = "30m"
  winrm_use_ssl  = false
  winrm_insecure = true

  # Boot from Windows ISO first, then hard disk
  boot      = "order=sata0;scsi0"
  boot_wait    = "5s"
  boot_command = ["<spacebar><spacebar><spacebar>"]

}

build {
  name    = "windows-server-2022"
  sources = ["source.proxmox-iso.windows-server"]

  # 1. Install remaining VirtIO drivers + QEMU Guest Agent
  provisioner "powershell" {
    scripts = ["./scripts/install-virtio.ps1"]
  }

  # 2. Configure WinRM for Ansible
  provisioner "powershell" {
    scripts = ["./scripts/setup-winrm.ps1"]
  }

  # 3. Upload Cloudbase-Init config files
  provisioner "file" {
    source      = "./config/cloudbase-init.conf"
    destination = "C:\\Windows\\Temp\\cloudbase-init.conf"
  }

  provisioner "file" {
    source      = "./config/cloudbase-init-unattend.conf"
    destination = "C:\\Windows\\Temp\\cloudbase-init-unattend.conf"
  }

  # 4. Install Cloudbase-Init and apply configs
  provisioner "powershell" {
    scripts = ["./scripts/install-cloudbase.ps1"]
  }

  # 5. Final cleanup
  provisioner "powershell" {
    scripts = ["./scripts/cleanup.ps1"]
  }

  # 6. Sysprep with Cloudbase-Init (generalizes the image + shuts down the VM)
  provisioner "powershell" {
    inline = [
      "& C:\\Windows\\System32\\Sysprep\\sysprep.exe /generalize /oobe /shutdown /unattend:\"C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\conf\\Unattend.xml\""
    ]
  }
}
