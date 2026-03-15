# --- Proxmox credentials ---

variable "proxmox_api_url" {
  type        = string
  description = "Proxmox API endpoint (e.g. https://10.0.0.10:8006/api2/json)"
}

variable "proxmox_username" {
  type        = string
  description = "Proxmox user (user@realm or user@realm!token)"
}

variable "proxmox_password" {
  type      = string
  sensitive = true
}

variable "admin_password" {
  type        = string
  description = "Windows Administrator password (used in autounattend + WinRM)"
  sensitive   = true
}

# --- VM template settings ---

variable "vm_name" {
  type    = string
  default = "windows-server-2022-template"
}

variable "disk_size" {
  type    = string
  default = "60G"
}

variable "memory" {
  type    = number
  default = 4096
}

variable "cpus" {
  type    = number
  default = 4
}

variable "proxmox_node" {
  type    = string
  default = "pve-01"
}

variable "storage_pool" {
  type        = string
  description = "Storage for VM disks (LVM-thin, e.g. local-lvm)"
  default     = "local-lvm"
}

variable "iso_storage_pool" {
  type        = string
  description = "Storage for ISO files (must be dir-type, e.g. local)"
  default     = "local"
}

variable "iso_file" {
  type        = string
  description = "Proxmox path to Windows Server 2022 ISO"
  default     = "local:iso/Windows_2022.iso"
}

variable "virtio_iso" {
  type        = string
  description = "Proxmox path to VirtIO drivers ISO"
  default     = "local:iso/virtio-win-0.1.285.iso"
}

# --- Build network (temporary static IP for Packer WinRM) ---

variable "build_ip" {
  type        = string
  description = "Temporary static IP assigned during build"
  default     = "10.0.0.100"
}

variable "build_netmask" {
  type    = string
  default = "255.255.255.0"
}

variable "build_gateway" {
  type    = string
  default = "10.0.0.1"
}

variable "build_dns" {
  type    = string
  default = "10.0.0.1"
}
