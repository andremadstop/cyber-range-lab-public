# Cyber-Range-Lab — Private Network + Subnetze
# 10.99.0.0/24 aufgeteilt in 4 funktionale Subnetze

resource "hcloud_network" "lab" {
  name     = "cyber-range-lab-net"
  ip_range = "10.99.0.0/24"
  labels = {
    component = "networking"
    lab       = "cyber-range"
  }
}

# DMZ-Subnet: Angreifbare Ziele (Web, Vault, Linux-Victim)
resource "hcloud_network_subnet" "dmz" {
  network_id   = hcloud_network.lab.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.99.10.0/28"
}

# BLUE-Subnet: SIEM + Blue-Team-Workstations
resource "hcloud_network_subnet" "blue" {
  network_id   = hcloud_network.lab.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.99.20.0/28"
}

# RED-Subnet: Kali-Linux-Workstations der Angreifer
resource "hcloud_network_subnet" "red" {
  network_id   = hcloud_network.lab.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.99.30.0/28"
}

# GM-Subnet: KI-Spielleiter + Headscale-Tailnet-Control-Plane
resource "hcloud_network_subnet" "gm" {
  network_id   = hcloud_network.lab.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.99.40.0/28"
}
