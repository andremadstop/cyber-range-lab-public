# Cyber-Range-Lab — Zielsysteme (DMZ-Subnet 10.99.10.0/28)
# 4 Server: Web-Target, Vault-Target, Linux-Victim, NC-Target
# Basis-Image: Debian 12 (hcloud images: debian-12)

locals {
  # Basis-SSH-Keys via SSH-Key-Namen (vorher in Hetzner-Projekt hinterlegt)
  ssh_key_ids = var.ssh_keys

  # Gemeinsame Labels fuer Target-Server
  target_labels = {
    component = "target"
    lab       = "cyber-range"
    subnet    = "dmz"
  }
}

# T1 — Web-Zielsystem (WordPress + Juice Shop)
resource "hcloud_server" "web_target" {
  name        = "web-target"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.target_labels, {
    role = "web-target"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.10.2"
  }
}

# T2 — Vault-Zielsystem (Vaultwarden, schwaches Master-PW)
resource "hcloud_server" "vault_target" {
  name        = "vault-target"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.target_labels, {
    role = "vault-target"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.10.3"
  }
}

# T3 — Linux-Victim (Lateral-Movement-Ziel + Mailhog)
resource "hcloud_server" "linux_victim" {
  name        = "linux-victim"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.target_labels, {
    role = "linux-victim"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.10.4"
  }
}

# T4 — NC-Target (Nextcloud-Victim mit Kundendaten)
resource "hcloud_server" "nc_target" {
  name        = "nc-target"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.target_labels, {
    role = "nc-target"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.10.5"
  }
}
