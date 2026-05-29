# Cyber-Range-Lab — Outputs fuer Ansible-Inventory-Generierung und Info

# DMZ-Subnet
output "web_target_ip" {
  value       = hcloud_server.web_target.ipv4_address
  description = "Private IP des Web-Zielsystems"
}
output "vault_target_ip" {
  value       = hcloud_server.vault_target.ipv4_address
  description = "Private IP des Vault-Zielsystems"
}
output "linux_victim_ip" {
  value       = hcloud_server.linux_victim.ipv4_address
  description = "Private IP des Linux-Victim"
}
output "nc_target_ip" {
  value       = hcloud_server.nc_target.ipv4_address
  description = "Private IP des Nextcloud-Zielsystems"
}

# BLUE-Subnet
output "wazuh_siem_ip" {
  value       = hcloud_server.wazuh_siem.ipv4_address
  description = "Private IP des Wazuh-SIEM"
}
output "blue_ws_ips" {
  value       = hcloud_server.blue_ws[*].ipv4_address
  description = "Private IPs der Blue-Team-Workstations"
}

# RED-Subnet
output "kali_andre_ip" {
  value       = hcloud_server.kali_andre.ipv4_address
  description = "Private IP der Kali-Andre-Workstation"
}
output "kali_user_ips" {
  value       = hcloud_server.kali_user[*].ipv4_address
  description = "Private IPs der Kali-User-Workstations"
}

# GM-Subnet
output "hermes_gm_ip" {
  value       = hcloud_server.hermes_gm.ipv4_address
  description = "Private IP des Hermes-GM-Spielleiters"
}
output "lab_headscale_ip" {
  value       = hcloud_server.lab_headscale.ipv4_address
  description = "Private IP der Headscale-Control-Plane"
}
output "lab_headscale_public_ip" {
  value       = hcloud_server.lab_headscale.ipv4_address
  description = "Public IP der Headscale-Control-Plane (Spieler-Onboarding)"
}

# Netzwerkinfo
output "network_id" {
  value       = hcloud_network.lab.id
  description = "ID des Private-Network"
}

# Uebersicht
output "server_count" {
  value       = 1 + var.team_size_red + var.team_size_blue
  description = "Anzahl der provisionierten Server (ohne hermes-gm, lab-headscale, wazuh-siem)"
}
output "total_servers" {
  value = {
    targets    = 4
    siem       = 1
    red_team   = var.team_size_red
    blue_team  = var.team_size_blue
    game_master = 2
    total      = 7 + var.team_size_red + var.team_size_blue
  }
  description = "Gesamtuebersicht aller Server"
}
