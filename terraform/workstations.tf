# Cyber-Range-Lab — Workstations
# RED-Subnet: Kali-Linux fuer Angreifer
# BLUE-Subnet: Ubuntu 22.04 + SIFT-Tools fuer Verteidiger

locals {
  red_labels = {
    component = "workstation"
    lab       = "cyber-range"
    subnet    = "red"
    team      = "red"
  }
  blue_labels = {
    component = "workstation"
    lab       = "cyber-range"
    subnet    = "blue"
    team      = "blue"
  }
}

# W1 — Kali-Andre (Red-Lead, Instructor)
resource "hcloud_server" "kali_andre" {
  name        = "kali-andre"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.red_labels, {
    role = "kali-andre"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.30.2"
  }
}

# W2-W4 — Kali-User (Red-Team-Mitglieder)
resource "hcloud_server" "kali_user" {
  count       = var.team_size_red - 1
  name        = "kali-user-${count.index + 1}"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.red_labels, {
    role  = "kali-user"
    index = "${count.index + 1}"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.30.${count.index + 3}"
  }
}

# W5-W7 — Blue-Workstations (Blue-Team-Mitglieder)
resource "hcloud_server" "blue_ws" {
  count       = var.team_size_blue
  name        = "blue-ws-${count.index + 1}"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.blue_labels, {
    role  = "blue-ws"
    index = "${count.index + 1}"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.20.${count.index + 3}"
  }
}
