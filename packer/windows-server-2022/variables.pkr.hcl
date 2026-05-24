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
  default = 8 
}
variable "vm_cpu_sockets" {
  type    = number
  default = 1
}
variable "vm_memory" {
  type    = number
  default = 8048
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
  type        = string
  default     = "Root123!"
  sensitive   = true
  description = "Mot de passe du compte Administrator Windows (WinRM + AutoLogon)"
}

variable "vm_ip" {
  type        = string
  default     = "192.168.30.15"
  description = "Adresse IP statique de la VM template"
}

variable "vm_network_prefix" {
  type        = number
  default     = 24
  description = "Longueur du préfixe réseau (ex: 24 pour /24)"
}

variable "vm_gateway" {
  type        = string
  default     = "10.0.0.1"
  description = "Passerelle par défaut de la VM"
}

variable "vm_dns" {
  type        = string
  default     = "10.0.0.1"
  description = "Serveur DNS de la VM"
}

variable "computer_name" {
  type        = string
  default     = "WIN-TEMPLATE"
  description = "Hostname de la machine Windows"
}

variable "timezone" {
  type        = string
  default     = "Romance Standard Time"
  description = "Fuseau horaire Windows (format Microsoft)"
}

variable "os_image_index" {
  type        = number
  default     = 2
  description = "Index de l'édition OS dans le WIM (Standard=2, Datacenter=4)"
}

variable "template_uuid" {
  type        = string
  default     = "10188f7c-e6f8-4e8c-9d83-530ea015e51e"
  description = "UUID de la VM template utilisé dans le script au démarrage"
}

variable "adaptive_endpoint" {
  type        = string
  default     = "http://127.0.0.1:8000"  
  description = "URL de l'endpoint d'Adaptive BYOL pour la collecte des données de provisioning"
}