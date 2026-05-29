# Cyber-Range-Lab — Variablen
# Version: 0.1 (Pilot)

variable "hcloud_token" {
  description = "Hetzner Cloud API-Token (wird nicht in Logs/Commits ausgegeben)"
  type        = string
  sensitive   = true
}

variable "team_size_red" {
  description = "Anzahl der Red-Team-Arbeitsstationen (Kali)"
  type        = number
  default     = 4
}

variable "team_size_blue" {
  description = "Anzahl der Blue-Team-Arbeitsstationen (SIFT-Tools)"
  type        = number
  default     = 3
}

variable "lab_lifetime_hours" {
  description = "Maximale Lebensdauer des Labs in Stunden — nach Ablauf stoppt der Cost-Watchdog"
  type        = number
  default     = 48
}

variable "ssh_keys" {
  description = "Liste der SSH-Key-Namen (laut Hetzner-API) fuer Root-Zugriff auf alle VMs"
  type        = list(string)
  default = [
    "cyber-range-lab-2026-05"
  ]
}

variable "location" {
  description = "Hetzner-Standort fuer alle Ressourcen"
  type        = string
  default     = "fsn1"
}
