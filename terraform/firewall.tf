# Cyber-Range-Lab — Cloud-Firewall
# Regeln aus docs/architecture.md Abschnitt "Netzwerk-Topologie"
#
# Architektur:
#   RED-Subnet  → DMZ-Subnet : allow all
#   RED-Subnet  → BLUE-Subnet: deny
#   BLUE-Subnet → DMZ-Subnet : allow tcp/22 + icmp
#   BLUE-Subnet → WAZUH      : allow tcp/443
#   GM-Subnet   → ALL        : allow all
#   DMZ-Subnet  → Internet   : allow all (Reverse-Shell-Callback)
#   ALL         → Headscale  : allow tcp/8080

resource "hcloud_firewall" "lab" {
  name = "cyber-range-lab-firewall"

  # Alle Subnetze muessen ICMP (Ping) gegenueber allen anderen duerfen
  rule {
    direction = "in"
    protocol  = "icmp"
    source_ips = [
      "10.99.10.0/28",
      "10.99.20.0/28",
      "10.99.30.0/28",
      "10.99.40.0/28",
    ]
    description = "ICMP zwischen allen Lab-Subnetzen"
  }

  # RED → DMZ: Allow all (Angriffe erlaubt)
  rule {
    direction       = "in"
    protocol        = "tcp"
    source_ips      = ["10.99.30.0/28"]
    destination_ips = ["10.99.10.0/28"]
    description     = "RED → DMZ: Angriffe erlaubt"
  }
  rule {
    direction       = "in"
    protocol        = "udp"
    source_ips      = ["10.99.30.0/28"]
    destination_ips = ["10.99.10.0/28"]
    description     = "RED → DMZ: Angriffe erlaubt (UDP)"
  }

  # BLUE → DMZ: Allow nur SSH + ICMP (Forensik)
  rule {
    direction       = "in"
    protocol        = "tcp"
    source_ips      = ["10.99.20.0/28"]
    destination_ips = ["10.99.10.0/28"]
    port            = "22"
    description     = "BLUE → DMZ: SSH nur fuer Forensik"
  }

  # BLUE → WAZUH: Allow HTTPS-Dashboard
  rule {
    direction       = "in"
    protocol        = "tcp"
    source_ips      = ["10.99.20.0/28"]
    destination_ips = ["10.99.20.2/32"]
    port            = "443"
    description     = "BLUE → WAZUH: Dashboard-Zugriff"
  }

  # ALL → Headscale: Allow Port 8080 (Control-Plane), nur intern
  rule {
    direction       = "in"
    protocol        = "tcp"
    source_ips      = [
      "10.99.10.0/28",
      "10.99.20.0/28",
      "10.99.30.0/28",
      "10.99.40.0/28",
    ]
    destination_ips = ["10.99.40.3/32"]
    port            = "8080"
    description     = "ALL → Headscale: Control-Plane"
  }

  # Headscale Public: allow HTTPS (443) + STUN (3478) von aussen
  # Fuer Spieler-Onboarding und Tailscale-Enroll
  rule {
    direction  = "in"
    protocol   = "tcp"
    source_ips = ["0.0.0.0/0", "::/0"]
    port       = "443"
    description = "Headscale Public: HTTPS fuer OIDC"
  }
  rule {
    direction  = "in"
    protocol   = "udp"
    source_ips = ["0.0.0.0/0", "::/0"]
    port       = "3478"
    description = "Headscale Public: STUN"
  }

  # GM-Subnet → ALL: Allow (Spielleiter sieht alles)
  # Wird durch die Default-Regel "allow from anywhere" auf GM-Hosts realisiert
  # explizit via apply_to fuer hermes-gm + lab-headscale

  # DMZ → Internet: Allow all (fuer Reverse-Shell-Callback)
  # Default-Regel: traffic to internet is allowed (keine explizite deny-Regel)
}
