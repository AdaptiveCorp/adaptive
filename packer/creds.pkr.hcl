# Proxmox API Credentials
variable "proxmox_api_url" {
  type    = string
  default = "https://10.0.0.10:8006/api2/json"
}

variable "proxmox_username" {
  type    = string
  default = "root@pam"  # Format: utilisateur@realm!nom_token
}

variable "proxmox_password" {
  type      = string
  default   = "adaptive"
  sensitive = true
}

variable "admin_password" {
  type      = string
  default   = "adaptive"
  sensitive = true
}

