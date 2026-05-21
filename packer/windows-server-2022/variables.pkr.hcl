variable "proxmox_url" {
  type = string
}
variable "proxmox_username" {
  type = string
}
variable "proxmox_password" {
  type      = string
  sensitive = true
}

variable "proxmox_skip_tls_verify" {
  type    = bool
  default = true
}
variable "proxmox_node" {
  type = string
}
variable "proxmox_storage" {
  type    = string
  default = "local-lvm"
}
variable "iso_storage_pool" {
  type    = string
  default = "local"
}
variable "iso_file" {
  type = string
}
# variable "iso_checksum" {
#   type = string
# }
variable "virtio_iso_file" {
  type    = string
  default = "local:iso/virtio-win.iso"
}
variable "vm_id" {
  type    = number
  default = 9000
}
variable "vm_name" {
  type    = string
  default = "tpl-windows-server-2022"
}
variable "template_description" {
  type    = string
  default = "Windows Server 2022 - VirtIO + Cloudbase-Init"
}
variable "vm_cpu_cores" {
  type    = number
  default = 2
}
variable "vm_cpu_sockets" {
  type    = number
  default = 1
}
variable "vm_memory" {
  type    = number
  default = 4096
}
variable "vm_disk_size" {
  type    = string
  default = "60G"
}
variable "network_bridge" {
  type    = string
  default = "vmbr0"
}
variable "winrm_username" {
  type    = string
  default = "Administrator"
}
variable "winrm_password" {
  type      = string
  sensitive = true
  default   = "P@cker2022!"
}
