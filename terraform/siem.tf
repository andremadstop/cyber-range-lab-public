# Cyber-Range-Lab — SIEM (Wazuh)
# BLUE-Subnet 10.99.20.0/28
# CX32: 4vCPU/8GB/80GB fuer Wazuh single-node

locals {
  siem_labels = {
    component = "siem"
    lab       = "cyber-range"
    subnet    = "blue"
  }
}

# S1 — Wazuh SIEM (Manager + Indexer + Dashboard)
resource "hcloud_server" "wazuh_siem" {
  name        = "wazuh-siem"
  server_type = "cx32"
  image       = "debian-12"
  location    = var.location
  labels = merge(local.siem_labels, {
    role = "wazuh-siem"
  })
  ssh_keys = local.ssh_key_ids

  network {
    network_id = hcloud_network.lab.id
    ip         = "10.99.20.2"
  }
}
