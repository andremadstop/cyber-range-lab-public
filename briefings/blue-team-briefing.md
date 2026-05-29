# Blue-Team-Briefing — Cyber-Range Pilot

> **Für:** Blue-Team (3 Personen) — der SOC der **Beispiel GmbH**
> **Spieltag:** Mo 2026-06-01 oder Di 2026-06-02
> **Lies das vor dem Warm-up.** Wazuh-Zugangsdaten bekommst du separat (Onboarding-DM / Handout).

---

## Deine Mission

Ihr seid die Verteidiger. Irgendwo im Lab arbeitet sich ein Red-Team durch eine Angriffskette.
Euer Job ist **nicht**, sie zu blocken (die Firewall trennt euch eh — `kein aktives Gegenfeuer`).
Euer Job ist:

1. **Detect** — Angriffsaktivität in Wazuh erkennen, sobald sie passiert.
2. **Investigate** — den Alert verstehen: Was? Wer? Wann? Wie schlimm?
3. **Document** — die Kill-Chain rekonstruieren und sauber festhalten.

Ihr habt **keinen Lösungsschlüssel** — und das ist Absicht. In einem echten SOC weiß niemand
vorher, was der Angreifer als Nächstes tut. Ihr arbeitet euch durch Telemetrie nach vorn. Genau
das ist die Fähigkeit, die ihr hier trainiert.

---

## Was ihr wisst (und was nicht)

**Ihr wisst:** Es gibt vier angreifbare Hosts im DMZ-Subnet `10.99.10.0/28` (Web, Vault,
Linux-Server, eine **Nextcloud mit Kundendaten**). Der Angriff folgt grob einer 6-Phasen-Kill-Chain
(Recon → Exfiltration). Diese Form kennt ihr aus dem Kurs (MITRE ATT&CK, Cyber-Kill-Chain).

**Ihr wisst nicht:** welche Exploits, welche CVEs, welchen Einstiegspfad Red wählt, oder welche
Daten Ziel sind. Das findet ihr raus — aus den Logs, nicht aus dem Briefing.

---

## Eure Werkzeuge

**Wazuh** ist euer SIEM. Dashboard: `https://wazuh-siem` (bzw. `https://10.99.20.2`, via Tailscale).
Login-Daten im Handout. Es zieht Logs aller DMZ-Targets + Workstations zusammen, korreliert sie zu
Alerts und macht File-Integrity-Monitoring (FIM).

Eure Blue-Workstations (`blue-ws-*`, `10.99.20.3–5`, Ubuntu 22.04) haben ein SIFT-Toolset:

| Tool | Wofür |
|---|---|
| `wazuh-dashboard` | Alert-Triage, Korrelation — dein Hauptarbeitsplatz |
| Zeek | Netzwerk-Telemetrie, Connection-Logs (`/opt/zeek/logs/current/`) |
| `tshark` / `tcpdump` | Packet-Level-Analyse, Live-Sniffing |
| Volatility 3 | Memory-Forensik (falls ihr ein Image bekommt) |
| `sigmac` | Sigma-Rules → Wazuh übersetzen |
| `jq` | JSON-Log-Verarbeitung |

**Firewall-relevant:** Ihr dürft `tcp/22` + `icmp` ins DMZ (Forensik-SSH, ping) und `tcp/443` zum
Wazuh-Dashboard. Ins RED-Subnet kommt ihr nicht — und müsst ihr auch nicht.

---

## Eure Lernziele (CySA+ CS0-003)

Daran messen wir den Erfolg im Debrief. Die Custom-Rules des Labs liegen im ID-Bereich
**`100010`–`100092`**. Eure Aufgabe ist, deren Trigger zu **finden und korrekt zu interpretieren** —
*nicht*, eine Rule-ID-Liste abzuhaken.

| ID | Lernziel | CySA+ | Worauf achten |
|---|---|---|---|
| **L1** | Brute-Force-Detection per SIEM-Korrelation | D1 SIEM-Use-Cases | Plötzliche 401-/Failed-Login-Häufungen |
| **L2** | Web-Exploit-Patterns in Logs (SQLi, LFI/RFI) | D1 Threat Hunting | Auffällige URL-/Payload-Muster |
| **L3** | Privilege Escalation + Persistence | D1 + D3 Host-Detection | FIM-Alerts (`cron`, `.ssh`), SUID, fremde Shares |
| **L4** | Lateral Movement + Exfiltration | D3 IR + Forensics | SSH von neuer Source, DNS-Anomalien, Mass-Download |

> **Bewusst KEIN Phasen→Rule-Mapping hier.** Ihr sollt die Verbindung „Alert → Angriffsphase"
> selbst herstellen. Wenn ihr eine Rule feuern seht, fragt euch: *Was bedeutet sie? Passt sie in
> eine größere Story?* Realistisch rutscht etwas durch — gerade L4 (Lateral Movement / „Valid
> Accounts"). Diese Lücken sind im Debrief der wertvollste Lernmoment.

**Tipp zum Start:** `rule.id >= 100010 AND rule.id <= 100092` zeigt euch alle Lab-Custom-Rules.
Sortiert nach Zeit, baut euch ein Bild — interpretiert dann.

---

## Euer Workflow (Threat-Hunting-Loop)

Arbeitet im Kreis, nicht linear:

1. **Baseline kennen.** Ein Traffic-Generator erzeugt ~100 Events/min (sonst leeres Dashboard).
   Verschafft euch früh ein Gefühl: *Was ist normal?* Erst dann erkennt ihr Abweichungen.
2. **Triage.** Neue Alerts nach Severity sortieren. Rauschen vs. echt?
3. **Pivot.** Bei einem echten Alert: Host? Source-IP? Zeitraum? Dashboard darauf filtern, schauen
   *was drumherum* passierte.
4. **Korrelieren.** Einzel-Alerts sind Punkte. Verbindet sie: „Scan → 401-Spike → erfolgreicher
   Login von derselben IP" = eine Story, kein Zufall.
5. **Dokumentieren.** Pro erkannter Phase: Was, wann, welche Rule, wie sicher? Nutzt PICERL.

### PICERL als roter Faden (NIST SP 800-61)

- **P**reparation — habt ihr (Wazuh läuft, Tools stehen)
- **I**dentification — *euer Hauptfokus heute:* erkennen + einordnen
- **C**ontainment / **E**radication / **R**ecovery — heute nur durchdenken („*was würden wir tun?*"),
  nicht real ausführen
- **L**essons Learned — der Debrief

---

## Hermes-GM — euer KI-Spielleiter

Im Telegram-Channel **`cyber-range-blue`** sitzt Hermes. Fragt ihn alles — **gestufte Hints** statt
Spoiler (Level 1 = Richtung, Level 2 = konkrete Query). Max. 6/Stunde pro Spieler.

- *„Wie finde ich failed SSH-Logins in Wazuh?"* → Query + Erklärung
- *„Dieser Alert vom Typ X — was bedeutet der?"* → Einordnung (kein „das war Red bei Phase D")
- *„Unterschied Rule vs. Decoder?"* → CySA+-Theorie

Hermes meldet sich auch **proaktiv**: feuert eine lernziel-relevante Rule, pingt er euch („Wazuh
hat gerade einen Alert vom Typ X — findet + interpretiert ihr ihn?"). Bei >120 min ohne neue
Aktivität schubst er an. Er verrät **nicht**, was Red tut — ihr seht Red nur durch die Telemetrie.

---

## Mindset

- **Ein Alert ist eine Hypothese, kein Urteil.** Verifizieren vor Eskalieren. False Positives
  gehören dazu (Baseline-Traffic).
- **Verstehen > Geschwindigkeit.** Lieber 5 Alerts richtig interpretiert als 50 durchgeklickt.
- **Teilt euch auf:** Live-Triage / Forensik-Tiefe / Kill-Chain-Doku. Rotiert.
- **Kein Wettbewerb gegen Red.** Im Debrief seht ihr ihre Sicht, sie eure.

Augen auf, Logs an. 🛡️
