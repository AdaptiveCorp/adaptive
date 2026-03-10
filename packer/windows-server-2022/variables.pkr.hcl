variable "proxmox_api_url" {
  type = string
}

variable "proxmox_username" {
  type = string
}

variable "proxmox_password" {
  type      = string
  sensitive = true
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "vm_name" {
  type    = string
  default = "WIN-SRV-2022"
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
  type    = string
  default = "local-lvm"
}

variable "iso_storage_pool" {
  type    = string
  default = "local"
}

variable "iso_file" {
  type    = string
  default = "local:iso/Windows_2022.iso"
}

variable "virtio_iso" {
  type    = string
  default = "local:iso/virtio-win-0.1.285.iso"
}

variable "network_bridge" {
  type    = string
  default = "vmbr0"
}

variable "vm_ip" {
  type    = string
  default = "10.0.0.50"
}

variable "vm_gateway" {
  type    = string
  default = "10.0.0.1"
}

variable "vm_netmask" {
  type    = string
  default = "255.255.255.0"
}

variable "vm_dns" {
  type    = string
  default = "8.8.8.8"
}
