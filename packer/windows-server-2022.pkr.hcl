packer {
  required_plugins {
    proxmox = {
      version = "~> 1.2"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

source "proxmox-iso" "windows-server" {
  # ── Proxmox connection ───────────────────────────────────────
  proxmox_url              = var.proxmox_api_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true
  node                     = var.proxmox_node

  # ── VM config ────────────────────────────────────────────────
  vm_name              = var.vm_name
  template_description = "Windows Server 2022 — WinRM + Cloudbase-Init (ADaptive)"
  memory               = var.memory
  cores                = var.cpus
  cpu_type             = "host"
  os                   = "win11"
  bios                 = "ovmf"
  machine              = "q35"
  qemu_agent           = true

  # ── EFI ──────────────────────────────────────────────────────
  efi_config {
    efi_storage_pool  = var.storage_pool
    pre_enrolled_keys = true
    efi_type          = "4m"
  }

  # ── Disk ─────────────────────────────────────────────────────
  disks {
    storage_pool = var.storage_pool
    type         = "scsi"
    disk_size    = var.disk_size
    format       = "raw"
    cache_mode   = "writeback"
  }

  scsi_controller = "virtio-scsi-pci"

  # ── Network ──────────────────────────────────────────────────
  network_adapters {
    model  = "virtio"
    bridge = var.network_bridge
  }

  # ── Windows ISO (boot) ──────────────────────────────────────
  boot_iso {
    iso_file = var.iso_file
    unmount  = true
    type     = "sata"
  }

  # ── VirtIO drivers ISO ──────────────────────────────────────
  additional_iso_files {
    type     = "sata"
    index    = 1
    iso_file = var.virtio_iso
    unmount  = true
  }

  # ── Autounattend (templated with variables) ─────────────────
  additional_iso_files {
    type         = "sata"
    index        = 2
    unmount      = true
    cd_label     = "OEMDRV"
    iso_storage_pool = var.storage_pool
    cd_content = {
      "autounattend.xml" = templatefile("${path.root}/autounattend.xml.pkrtpl.hcl", {
        admin_password = var.admin_password
        vm_ip          = var.vm_ip
        vm_gateway     = var.vm_gateway
        vm_netmask     = var.vm_netmask
        vm_dns         = var.vm_dns
      })
    }
  }

  # ── WinRM communicator ──────────────────────────────────────
  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_password = var.admin_password
  winrm_timeout  = "1h"
  winrm_use_ssl  = false
  winrm_insecure = true

  # ── Boot ─────────────────────────────────────────────────────
  boot_wait    = "3s"
  boot_command = ["<spacebar>"]

  # ── Cloud-Init drive (Proxmox will use this slot on clones) ─
  cloud_init              = true
  cloud_init_storage_pool = var.storage_pool
}


build {
  name    = "windows-server-2022"
  sources = ["source.proxmox-iso.windows-server"]

  # 1. VirtIO drivers (balloon, serial, QEMU guest agent)
  provisioner "powershell" {
    script = "${path.root}/scripts/install-virtio.ps1"
  }

  # 2. WinRM hardening for Ansible (HTTPS + CredSSP)
  provisioner "powershell" {
    script = "${path.root}/scripts/setup-winrm.ps1"
  }

  # 3. Cloudbase-Init (handles IP/hostname on clone via Proxmox cloud-init)
  provisioner "powershell" {
    script = "${path.root}/scripts/install-cloudbase.ps1"
  }

  # 4. Cleanup temp files and logs
  provisioner "powershell" {
    script = "${path.root}/scripts/cleanup.ps1"
  }
}
