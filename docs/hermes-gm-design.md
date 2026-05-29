# Hermes-GM Skill — Design-Spezifikation

> **Spec-ID**: CRL-HERMES-GM-001
> **Version**: 0.1 (Voll-Scope Phase 1)
> **Datum**: 2026-05-28
> **Tag**: training-lab

## Zweck

Hermes-Skill, der als neutraler KI-Spielleiter fungiert. Beide Teams (Red + Blue) kommunizieren ueber
Telegram-Channels mit ihm. Er kennt Attack-Chain + Detection-Rules + MITRE-ATT&CK + Spielerprofile.

**Pflicht-Versprechen**: Andre kann am Spieltag voll Spieler sein, nicht Game-Master.

## Funktionsbereiche

### 1. Pull-Mode (Spieler fragen, Hermes antwortet)

**Trigger**: Direktnachricht in Telegram-Channel `cyber-range-red` oder `cyber-range-blue`.

**Beispiele**:
- Red: „Wie umgeh ich die WAF auf web-target?" -> Hint mit gestufter Spoiler-Tiefe
- Blue: „Wie finde ich failed SSH in Wazuh?" -> Wazuh-Query + Erklaerung
- Beide: „Was war nochmal Pyramid of Pain?" -> CySA+-Konzept-Erklaerung

**Verhalten**: Hermes antwortet team-spezifisch, gibt KEINE Spoiler an andere Seite weiter.
GM-Channel `cyber-range-gm` (Andre) sieht alles und kann override-en.

### 2. Push-Mode (Hermes proaktiv)

**Trigger**: Poll-Loop alle 2 min:

- Wazuh-API: gibt es neue Alerts? Welche getriggert? Wer hat sie gesehen?
- Hetzner-API: laufen alle VMs? CPU/RAM-Anomalien?
- Telegram: gibt es seit X min keine Aktivitaet in einem Team-Channel?

**Aktionen**:
- **Stillstand-Erkennung**: Blue >30 min keine neue Wazuh-Query, Red >30 min keine neue Verbindung
  zu Targets -> proaktiver Hint mit gestufter Schwierigkeit
- **Eskalation**: wenn Red zu schnell durch Phase X -> Schwierigkeit erhoehen (z.B. zusaetzliche
  WAF-Rule aktivieren, neuen Brute-Force-Lockout-Timer)
- **Detection-Highlight**: wenn neuer Wazuh-Alert getriggert, der Blue-Lernziel betrifft -> ping
  Blue-Channel „Wazuh hat gerade einen Alert vom Typ X erkannt — koennt ihr ihn finden und
  interpretieren?"

### 3. Honcho-Spielerprofile (adaptiv)

**Datenmodell pro Spieler** (gespeichert in Honcho):

```yaml
player_id: andre-mitschueler-1
team: blue
skill_level_inferred:
  siem: 3  # 1-5, derived from question quality
  forensics: 2
  network: 4
hints_received_today: 5
hints_helpful_ratio: 0.8  # explizit oder implizit
last_active: 2026-06-01T14:23:00Z
favorite_tools: [wazuh-dashboard, sigmac]
struggling_with: [memory-forensics, dns-tunneling]
```

**Verhalten**:
- Anfaenger bekommen mehr Kontext + naehere Beispiele
- Fortgeschrittene bekommen sokratische Gegenfragen statt direkter Antworten
- Profile persistent ueber Sessions hinaus (Andre's CySA+-Sparring nutzt gleiche Profile)

### 4. Auto-Lessons-Learned-Report

**Trigger**: Manuell via `/report` durch Andre/Game-Master, oder automatisch beim `make lab-down`.

**Inhalt** (generiert via Gemini 2.5 Pro aus Wazuh-Log-Dump + Telegram-Channel-History):

```markdown
# Lessons Learned — {Datum, Spielername-Liste}

## Executive Summary
- Spielzeit: X h
- Red-Erfolg: Phase A-F erreicht? Welche?
- Blue-Erfolg: Alerts erkannt / korrekt interpretiert / verpasst
- Gesamturteil: Red gewinnt / Blue gewinnt / Draw

## MITRE-ATT&CK-Heatmap
- T1110.001 (Password Brute Force) — Red ausgefuehrt, Blue erkannt nach 4 min ✓
- T1078 (Valid Accounts) — Red ausgefuehrt, Blue NICHT erkannt ✗
- ...

## Detection-Rule-Trigger-Statistik
- Wazuh Rule 5712: 47 Trigger, Blue investigated 12 (26%)
- Custom-Rule custom-ssh-new-source: 3 Trigger, Blue investigated 3 (100%)
- ...

## Was Blue verpasst hat (kritische Misses)
- Phase D Persistence: Cron-Backdoor war via FIM-Rule getriggert,
  aber Blue hat den Alert nicht im Dashboard gefunden — Such-Filter-Problem.
- Phase F Exfiltration: DNS-Tunneling lief ueber 8 min, kein Blue-Spieler
  hat auf die DNS-Anomaly-Rule reagiert.

## Was Red gut gemacht hat
- Pfad B2 (Juice-Shop-SQLi) elegant durchgespielt, sqlmap mit --random-agent.
- Phase E (Lateral Movement) effiziente Trophy-Secret-Extraktion.

## Empfehlungen fuer naechsten Run
- Blue-Team: Wazuh-Dashboard Custom-View fuer FIM-Alerts einrichten
- Red-Team: subtiler vorgehen bei Brute-Force (Rate-Limit-Bewusstsein)
- Lab: zusaetzliche WAF-Rule fuer Phase B (Schwierigkeit hoch)
```

**Output**: Markdown-Datei + PDF in `lessons-learned/YYYY-MM-DD-runname.md`,
zusaetzlich Telegram-Post in GM-Channel.

## Architektur

```
            ┌──────────────────────────────────────┐
            │  hermes-gm CX22 (Hetzner)            │
            │                                       │
            │  ┌────────────────────────────────┐  │
            │  │ Hermes 0.14 Agent              │  │
            │  │  + Skill: cyber-range-gm       │  │
            │  └──┬─────────────────────────────┘  │
            │     │                                 │
            │  ┌──▼──────────────────────────────┐ │
            │  │ Skill Modules (Python)          │ │
            │  │  • gm_context.yaml (static)     │ │
            │  │  • wazuh_poller.py              │ │
            │  │  • telegram_router.py           │ │
            │  │  • honcho_client.py             │ │
            │  │  • hint_policy.py               │ │
            │  │  • report_generator.py          │ │
            │  │  • llm_provider.py (Gemini)     │ │
            │  └──┬─────────────────────────────┬─┘ │
            │     │                              │  │
            └─────┼──────────────────────────────┼──┘
                  │                              │
        ┌─────────┼──────────┐         ┌─────────┼────────┐
        │ wazuh-siem (API)   │         │ Telegram Bot     │
        │ + Hetzner API      │         │ @your-telegram   │
        │ + Honcho (internem Host) │         │ -bot    │
        └────────────────────┘         └──────────────────┘
```

## Skill-Code-Struktur

```
hermes-gm-skill/
├── SKILL.md                    # Manifest fuer Hermes (skill-metadata)
├── pyproject.toml              # Python-Deps
├── gm_context.yaml             # Statischer Spiel-Kontext (Attack-Chain, Rules, MITRE-Map)
├── prompts/
│   ├── system.j2               # Haupt-System-Prompt
│   ├── red_hint.j2             # Red-Hint-Template
│   ├── blue_hint.j2            # Blue-Hint-Template
│   └── report.j2               # Lessons-Learned-Template
├── modules/
│   ├── __init__.py
│   ├── wazuh_poller.py         # Polls Wazuh-API alle 2min
│   ├── telegram_router.py      # 3 Channels (red/blue/gm) routing
│   ├── honcho_client.py        # Spielerprofile lesen/schreiben
│   ├── hint_policy.py          # Stillstand-Erkennung + Hint-Eskalation
│   ├── report_generator.py     # Lessons-Learned-Generator
│   ├── llm_provider.py         # Gemini/Codestral-Adapter
│   └── safety_filter.py        # Verhindert Token-Leaks in Outputs
├── tests/
│   ├── test_hint_policy.py
│   ├── test_wazuh_poller.py
│   └── fixtures/
└── README.md                   # Setup, Run, Tests
```

## Externe Abhaengigkeiten

| Service | Wofuer | Wie verbunden |
|---|---|---|
| Wazuh API | Alerts + Logs polling | REST + JWT-Token |
| Honcho (einem internen Host) | Spielerprofile + Theory-of-Mind | gRPC |
| Telegram Bot API | Channels Red/Blue/GM | python-telegram-bot |
| Gemini API (2.5 Flash + Pro) | LLM-Inference | google.genai SDK |
| Hetzner Cloud API | VM-Status, Anomalien | hcloud Python SDK |

## Sicherheits-Constraints

1. **Token-Leak-Pflicht-Filter** — `safety_filter.py` scant alle Outbound-Messages auf
   regex-Patterns (API-Keys, JWTs, SSH-Keys), redact-ed automatisch
2. **Honcho-Spielerprofile pseudonymisiert** — Klarnamen NIE in Honcho, nur `player-id-uuid`
3. **GM-Channel-Override** — Andre kann via Telegram-Befehl `/override mute red 10m` einzelne
   Channels stummschalten oder Hint-Politik anpassen
4. **DSGVO** — Spielerprofile loeschbar via `/forget-me`, Reports nur mit expliziter Einwilligung
   archivieren (Pilot: alle Mitschueler stimmen zu via Uebungsvereinbarung)
5. **LLM-Cost-Cap** — pro Iteration Hard-Stop bei 5 € LLM-Spend (entspricht ~50M Tokens
   Gemini-Flash, deutlich mehr als realer Bedarf)

## Honcho-Integration (Detail)

**Honcho-App**: `cyber-range-coach` (neu, separate App von Andre's bestehenden)

**Sessions**:
- `pilot-2026-06-01` (Spieltag-Session, alle 8 Spieler in einer Session)
- Persistente User-Profile ueber Sessions hinweg (gleicher Spieler kommt in 3 Months wieder)

**Theory-of-Mind**:
- Honcho-Deriver beobachtet Spieler-Fragen, schaetzt Skill-Level + Lerntempo
- Hermes-GM nutzt Honcho-Insights um Hint-Tiefe zu kalibrieren

**Fallback bei Honcho-Ausfall**: Hermes-GM faehrt im Stateless-Mode weiter (alle Spieler
gleich behandelt), kein Spielabbruch.

## Auto-Report-Generierung (Detail)

**Inputs**:
- Wazuh-API-Dump aller Alerts im Spielzeitraum (JSON)
- Telegram-Channel-History (Red + Blue + GM)
- Honcho-Session-Insights (welche Spieler haben mit welchen Themen gestrugglet)
- Statischer Spielkontext aus `gm_context.yaml`

**Pipeline**:
1. Wazuh-Alerts klassifizieren nach MITRE-Technique (Mapping in `gm_context.yaml`)
2. Per Phase A-F: was lief wann, wer hat reagiert
3. Detection-Coverage berechnen (% Alerts die Blue investigated hat)
4. Gemini 2.5 Pro Call mit allen Inputs + `prompts/report.j2`-Template
5. Markdown rendern, PDF via pandoc, in `lessons-learned/` ablegen
6. Telegram-Post mit TL;DR + Link zu vollem Report

**Kosten pro Report**: ~30-50k Tokens In + 5k Out = ca. 0.06 € pro Report.

## Test-Strategie

- **Unit-Tests**: `pytest` fuer Module einzeln (mocked APIs)
- **Integration-Tests**: docker-compose mit Mock-Wazuh + Telegram-Test-Bot
- **Dry-Run vor Pilot**: am So-Abend End-to-End-Test mit Andre allein
  (Andre spielt Red + Blue in 2 Browser-Tabs, sieht ob Hermes-GM korrekt reagiert)

## Open Questions

- [ ] Honcho-Setup auf internem Host (separates Honcho fuer Lab) oder bestehendes auf internem Host reuse?
  -> Empfehlung: separates fuer DSGVO-Isolation
- [ ] Hint-Cooldown: wie lange zwischen 2 Hints fuer gleichen Spieler?
  -> Default 5 min, konfigurierbar
- [ ] Sprache: Hermes-GM antwortet auf Deutsch oder Englisch?
  -> Default Deutsch (Mitschueler-Sprache), CySA+-Fachbegriffe Englisch belassen

## Referenzen

- Hermes-Agent Docs: https://github.com/NousResearch/hermes-agent
- Honcho Docs: https://docs.honcho.dev/
- Andre's bestehende Hermes-Skills als Pattern-Referenz:
  - home-assistant-operations
  - vault-inbox-capture
  - vikunja-task
