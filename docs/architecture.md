# Cyber-Range Lab — Architektur-Spezifikation

> **Spec-ID**: CRL-ARCH-001
> **Version**: 0.1 (Pilot)
> **Datum**: 2026-05-28
> **Status**: Draft, in Review

## Zweck

Spezifikation einer reproduzierbaren Trainings-Cyber-Range fuer Red-Team-vs-Blue-Team-Uebungen.
Ziel: Wochenend-Format, 4-8 Teilnehmer, voll automatisierter Tear-up/Tear-down, KI-Spielleitung.

## Design-Prinzipien

1. **Detection-Rule-First-Design** — Wazuh-Detection-Rules werden ZUERST definiert,
   Attack-Chain dahinter konzipiert, Verwundbarkeiten daraus abgeleitet. Niemals umgekehrt.
2. **Harte Tailnet-Isolation** — Lab-Headscale ist separate Instanz, eigene ACL,
   keine Bridge zum bestehenden Tailnet/AdGuard.
3. **Reuse > Reinvent** — Verwundbarkeiten aus Vulhub/HTB, Detection-Rules aus DetectionLab/SigmaHQ,
   Hermes-Skill-Pattern aus bestehenden Skills (home-assistant-operations, vault-inbox-capture).
4. **Hourly-Cost-Disziplin** — VMs nur fuer Spieldauer, Snapshot-Strategie statt Dauerbetrieb.
5. **Reproduzierbarkeit als Asset** — alles IaC, alles versioniert, One-Command-Deploy.

## Netzwerk-Topologie

> **Architektur-Prinzip: 100% Hetzner-Cloud, kein Proxmox-Footprint.**
> Lab ist komplett vom Homelab isoliert — Blast-Radius bleibt im Hetzner-Projekt.
> Portabel: laeuft ohne Proxmox-Abhaengigkeit auf einem eigenen Cloud-Account.

```
                  ┌────────────────────────────────────────────┐
                  │ Hetzner-Cloud-Lab                          │
                  │ Project: "cyber-range-lab"                 │
                  │ Private Network: 10.99.0.0/24              │
                  │                                            │
                  │  ┌─────────────────────────────────────┐  │
                  │  │ DMZ-Subnet 10.99.10.0/28            │  │
                  │  │  • web-target    CX22 10.99.10.2    │  │
                  │  │  • vault-target  CX21 10.99.10.3    │  │
                  │  │  • linux-victim  CX22 10.99.10.4    │  │
                  │  └─────────────────────────────────────┘  │
                  │                                            │
                  │  ┌─────────────────────────────────────┐  │
                  │  │ BLUE-Subnet 10.99.20.0/28           │  │
                  │  │  • wazuh-siem    CX31 10.99.20.2    │  │
                  │  │  • blue-ws-1..4  CX22 10.99.20.3..6 │  │
                  │  └─────────────────────────────────────┘  │
                  │                                            │
                  │  ┌─────────────────────────────────────┐  │
                  │  │ RED-Subnet 10.99.30.0/28            │  │
                  │  │  • kali-andre    CX22 10.99.30.2    │  │
                  │  │  • kali-user-1..3 CX22 10.99.30.3..5│  │
                  │  └─────────────────────────────────────┘  │
                  │                                            │
                  │  ┌─────────────────────────────────────┐  │
                  │  │ GM-Subnet 10.99.40.0/28             │  │
                  │  │  • hermes-gm     CX22 10.99.40.2    │  │
                  │  │    (KI-Spielleiter, eigene Hermes-  │  │
                  │  │     Instance, isolierte Tokens)     │  │
                  │  │  • lab-headscale CX22 10.99.40.3    │  │
                  │  │    (Tailnet-Control-Plane, eigene   │  │
                  │  │     ACL, ephemeral Pre-Auth-Keys,   │  │
                  │  │     Public-IP fuer Spieler-Enroll)  │  │
                  │  └─────────────────────────────────────┘  │
                  └────────────────────────────────────────────┘

Firewall-Regeln (Hetzner Cloud Firewall):
  RED-Subnet  → DMZ-Subnet : allow all (Angriffe erlaubt)
  RED-Subnet  → BLUE-Subnet: deny (kein Cheat-Path)
  BLUE-Subnet → DMZ-Subnet : allow tcp/22, allow icmp (Forensik)
  BLUE-Subnet → WAZUH      : allow tcp/443 (Dashboard)
  GM-Subnet   → ALL        : allow (Spielleiter sieht alles)
  DMZ-Subnet  → Internet   : allow (Reverse-Shell-Callback ermoeglicht)
  ALL         → Headscale  : allow tcp/8080 (control-plane)
```

## Komponenten-Inventar

| ID | Hostname | Provider | Sizing | Rolle | Software |
|---|---|---|---|---|---|
| T1 | web-target | Hetzner CX22 | 2vCPU/4GB/40GB | Web-Zielsystem | Juice Shop (Docker) + WordPress 5.4 mit Slider Revolution 4.1 (CVE-2014-9734) |
| T2 | vault-target | Hetzner CX22 | 2vCPU/4GB/40GB | Passwort-Zielsystem | Vaultwarden, schwaches Master-PW (Top-1000-Liste), Trophy-Secret "ssh-key-linux-victim" |
| T3 | linux-victim | Hetzner CX22 | 2vCPU/4GB/40GB | Lateral-Movement-Ziel + Mail | Apache + auditd + SUID-Binary (`/usr/bin/find -perm 4755`), Cron-Misconfig, Trophy-File `/opt/secret/flag.txt`, Mailhog |
| S1 | wazuh-siem | Hetzner CX32 | 4vCPU/8GB/80GB | SIEM | Wazuh 4.7 single-node (Manager + Indexer + Dashboard), pre-tuned Rules, Baseline-Traffic-Generator |
| W1-W4 | kali-* | Hetzner CX22 × 4 | 2vCPU/4GB/40GB | Red-Workstations | Kali Linux Docker-Image + tmux + User-Account je Mitschueler |
| W5-W7 | blue-ws-* | Hetzner CX22 × 3 | 2vCPU/4GB/40GB | Blue-Workstations | Ubuntu 22.04 + SIFT-Tools (Volatility 3, Zeek, Wireshark-CLI, sigmac, jq) |
| GM | hermes-gm | Hetzner CX22 | 2vCPU/4GB/40GB | KI-Spielleiter | Hermes 0.14 + Skill „cyber-range-gm" + Honcho-Client + Telegram-Bridge |
| HS | lab-headscale | Hetzner CX22 | 2vCPU/4GB/40GB | Tailnet-Control-Plane | Headscale 0.23, eigene ACL-Datei, ephemeral Pre-Auth-Keys, Public-IP fuer Spieler-Enroll |

**Total: 13 Hetzner-VMs** (Setup mit Co-GM als Senior-GM Co-Pilot, keine eigene Blue-WS, kein Proxmox-Footprint).

> **Fallback Option A** falls Co-GM Co-GM-Rolle ablehnt und Blue-Lead spielen will: +1 Blue-WS (`blue-ws-co-gm`), Total 13 VMs.

## Kostenkalkulation

**Hourly-Modell** (Hetzner Cloud, Stand 2026-05):

| Sizing | €/h | × Anzahl | €/h Total | €/48h |
|---|---|---|---|---|
| CX22 (2vCPU/4GB/40GB) | 0.007 | 11 (web, vault, linux-victim, 4 Kali, 3 Blue-WS, hermes-gm, lab-headscale) | 0.077 | 3.70 |
| CX32 (4vCPU/8GB/80GB) | 0.013 | 1 (wazuh-siem) | 0.013 | 0.62 |
| Snapshots (3 × 5GB-avg) | — | — | — | 0.50 |
| Private Network | gratis | 1 | 0.000 | 0.00 |
| **Total** | | | **0.090** | **~4.82** |

Plus Object-Storage fuer Snapshot-Archiv: ~0.20 €/Mo flat fuer den Pilot.

**Pilot Mo/Di Spieltag mit 48h Lifetime**: **~5 €** Cloud-Kosten.

**Dauerhaft 30 Tage liefen wuerde**: ~60 €/Mo — wird NICHT gemacht, Tear-down nach jedem Run.

**Fallback Option A** (Co-GM als Blue-Lead): +1 CX22 = +0.34 €/48h, Total ~5 €.

> ⚠ **Preisanpassung Hetzner ab 15. Juni 2026**: Neue Tarife fuer Cloud Server bei
> Neubestellungen + Rescales. Bestehende Server unveraendert, aber unser Lab wird
> jede Iteration neu erstellt → spaetere Pilots ggf. teurer.
> Quelle: Hetzner-Newsfeed 28.05.2026, Pressemeldung beim Console-Login.

## Detection-Rule-First Lernziele

| ID | Lernziel | CySA+-Bezug | Wazuh-Rules (Stand) |
|---|---|---|---|
| L1 | SIEM-Korrelation fuer Brute-Force-Detection (Spike-Erkennung) | D1 SIEM-Use-Cases | Rule 5712 (web 401 brute), custom-ssh-brute |
| L2 | Web-Exploit-Patterns in Apache-Logs (SQLi, RFI, LFI) | D1 Threat Hunting | apache-rules 31100-31199, custom-sqli |
| L3 | Privilege Escalation + Persistence (Cron, SUID, authorized_keys) | D1 + D3 Host-Detection | FIM-Rules auf /etc/cron.d, /root/.ssh, custom-sudo-anomaly |
| L4 | Lateral Movement + Exfiltration aus Netzwerk-Telemetrie | D3 IR + Forensics | Rule custom-ssh-new-source, custom-dns-tunneling |

Detail-Implementierung: `docs/detection-rules.md` (geschrieben von Hermes).

## Attack-Chain (6 Phasen)

Siehe `docs/attack-chain.md` (geschrieben von Hermes).

Kurzform:
- **A** Recon (20 min) — nmap, gobuster, banner-grabbing
- **B** Initial Access (60 min, 3 Pfade) — WP-Brute / Juice-Shop-SQLi / Vault-PW-Raten
- **C** Privilege Escalation (30 min) — Slider-Revolution-RCE + SUID-find
- **D** Persistence (20 min) — Cron-Backdoor + SSH-Key-Drop
- **E** Lateral Movement (30 min) — Trophy-Secret -> SSH zu linux-victim
- **F** Exfiltration (20 min) — Trophy-File via HTTPS-POST oder DNS-Tunneling

## Hermes-GM (KI-Spielleiter)

**Voll-Scope Phase 1 (Pilot):**

- Pull-Mode: beide Teams haben Telegram-Channel mit Hermes, fragen aktiv
- Push-Mode: pollt Wazuh-API alle 2 min, erkennt Stillstand (>30 min keine neuen Alerts), schickt unprompted Hints
- Honcho-Integration: fuehrt Spielerprofile (Skill-Level, Lernfortschritt), gibt adaptive Hints
- Auto-Report: generiert Lessons-Learned-Report nach Spielende (MITRE-Heatmap, Rule-Trigger-Statistik, Was-hat-Blue-verpasst)
- LLM: Gemini 2.5 Flash Default, Gemini 2.5 Pro fuer Report-Generierung

Detail-Spec: `docs/hermes-gm-design.md`.

## Sicherheits-Constraints

1. **Lab-Tailnet komplett separate Headscale-Instanz** — keine Bridge zum bestehenden Tailnet.
2. **Lab-Tokens ephemeral** — Pre-Auth-Keys 72h Expiry, nicht reusable.
3. **Hetzner-Projekt isoliert** — separates Projekt „cyber-range-lab" mit Budget-Cap 50 € Hard-Stop.
4. **Token-Logging-Filter** — Hermes darf keine Tokens in Logs/Telegram-Outputs leaken (siehe `feedback_secret_handling.md`).
5. **DMZ-Internet-Zugang via Cloud-Firewall steuerbar** — Default offen (Reverse-Shell ermoeglicht), zu fuer air-gapped-Runs.
6. **Snapshot-Archivierung in Object Storage** — keine Customer-Daten in Snapshots ohne DSGVO-Pruefung.
7. **Vor Spielbeginn schriftliche Uebungsvereinbarung mit allen Teilnehmern** — Template in `docs/uebungsvereinbarung.md`.

## Spielablauf (8h-Spieltag)

| Block | Dauer | Inhalt |
|---|---|---|
| Tear-up | 30 min | `make lab-up`, Headscale-Auth fuer alle Spieler |
| Warm-up | 90 min | Gemeinsamer Tool-Walkthrough, Team-Briefing getrennt |
| Runde 1 | 2.5 h | Phase A-C (Recon, Initial Access, Priv-Esc) |
| Zwischenanalyse | 30 min | Hermes-GM-Snapshot, Hints, Eskalation |
| Runde 2 | 2.5 h | Phase D-F (Persistence, Lateral, Exfil) |
| Debrief | 1 h | Hermes-Auto-Report, gemeinsame Lessons Learned |

## Open Questions / Risks

- [ ] Pre-Auth-Key-Rotation: nach jedem Spieler-Onboarding ablaufen lassen oder Lifetime-Key fuer Spielzeit?
- [ ] Hermes-GM-LLM-Fallback wenn Gemini-Quota erschoepft: auf Haiku 4.5 oder Codestral?
- [ ] Backup-Plan wenn Hetzner-Region ausfaellt (sehr unwahrscheinlich, aber Spielzeit waere weg)?
- [ ] Mitschueler-Onboarding-Friction: wer hat noch nie Tailscale installiert? -> Loom-Video-Walkthrough nice-to-have

## Glossar

- **DMZ** — Demilitarisierte Zone, hier Subnet mit angreifbaren Zielen
- **SIEM** — Security Information & Event Management (Wazuh in unserem Setup)
- **FIM** — File Integrity Monitoring (Wazuh-Feature)
- **PICERL** — Preparation/Identification/Containment/Eradication/Recovery/Lessons (NIST SP 800-61)
- **Trophy-File/Secret** — Datei oder Credential das Red-Team „erbeuten" muss als Erfolgskriterium

## Referenzen

- CySA+ CS0-003 Exam Objectives
- Wazuh Documentation: https://documentation.wazuh.com/
- DetectionLab: https://github.com/chrissanders/DetectionLab
- Vulhub: https://github.com/vulhub/vulhub
- SigmaHQ Rules: https://github.com/SigmaHQ/sigma
- HTB Starting Point: https://app.hackthebox.com/starting-point
- NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide
