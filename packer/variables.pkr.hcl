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
  default = "pve-01"  # Nom de votre nœud Proxmox
}

variable "storage_pool" {
  type    = string
  default = "local-lvm"
}

variable "iso_file" {
  type    = string
  default = "local:iso/Windows_2022.iso"  # Chemin ISO Windows
}

variable "virtio_iso" {
  type    = string
  default = "local:iso/virtio-win-0.1.285.iso"
}

