# Cyber-Range-Lab — Spielleiter-Infrastruktur
# GM-Subnet 10.99.40.0/28

locals {
  gm_labels = {
    component = "game-master"
    lab       = "cyber-range"
    subnet    = "gm"
  }
}

# GM — KI-Spielleiter (Hermes + Honcho + Telegram-Bridge)
resource "hcloud_server" "hermes_gm" {
  name        = "hermes-gm"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.gm_labels, {
    role = "hermes-gm"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.40.2"
  }
}

# HS — Headscale-Tailnet-Control-Plane
# Eigene Public-IP fuer Spieler-Onboarding
resource "hcloud_server" "lab_headscale" {
  name        = "lab-headscale"
  server_type = "cx22"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.gm_labels, {
    role = "lab-headscale"
  })
  ssh_keys = local.ssh_key_ids

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.40.3"
  }
}
