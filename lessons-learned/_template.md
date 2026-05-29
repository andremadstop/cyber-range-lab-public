# Lessons Learned — {{ run_date }}

> Auto-generiert von Hermes-GM nach Spielende.
> Kann manuell ergaenzt werden.

## Run-Metadaten

- **Datum**: {{ run_date }}
- **Spielzeit**: {{ duration_hours }} h
- **Red-Team**: {{ red_players }}
- **Blue-Team**: {{ blue_players }}
- **Game-Master**: Hermes-GM + {{ human_gm }}
- **Lab-Version**: {{ lab_version }}
- **Gesamt-Cloud-Kosten**: {{ cloud_cost }} €

## Executive Summary

{{ exec_summary }}

## MITRE-ATT&CK-Heatmap

| Technique | Red ausgefuehrt | Blue erkannt | Reaktionszeit |
|---|---|---|---|
| T1110.001 Brute Force | {{ }} | {{ }} | {{ }} |
| T1078 Valid Accounts | {{ }} | {{ }} | {{ }} |
| T1055 Process Injection | {{ }} | {{ }} | {{ }} |
| T1059.004 Unix Shell | {{ }} | {{ }} | {{ }} |
| T1053.003 Scheduled Task | {{ }} | {{ }} | {{ }} |
| T1098.004 SSH Authorized Keys | {{ }} | {{ }} | {{ }} |
| T1021.004 SSH | {{ }} | {{ }} | {{ }} |
| T1572 Protocol Tunneling | {{ }} | {{ }} | {{ }} |

## Detection-Rule-Trigger-Statistik

| Rule ID | Trigger Count | Blue investigated | Coverage |
|---|---|---|---|
| Wazuh 5712 (web brute) | {{ }} | {{ }} | {{ }} % |
| custom-ssh-brute | {{ }} | {{ }} | {{ }} % |
| apache-sqli | {{ }} | {{ }} | {{ }} % |
| fim-cron-modified | {{ }} | {{ }} | {{ }} % |
| fim-authorized-keys | {{ }} | {{ }} | {{ }} % |
| custom-ssh-new-source | {{ }} | {{ }} | {{ }} % |
| custom-dns-anomaly | {{ }} | {{ }} | {{ }} % |

## Was Blue verpasst hat (kritische Misses)

{{ blue_misses }}

## Was Red gut gemacht hat

{{ red_wins }}

## Was Blue gut gemacht hat

{{ blue_wins }}

## Was Red versemmelt hat

{{ red_misses }}

## Spielerprofile (anonymisiert)

| Player | Team | Skill-Wachstum | Bemerkung |
|---|---|---|---|
| {{ }} | {{ }} | {{ }} | {{ }} |

## Hermes-GM-Performance

- Hints insgesamt: {{ }}
- Davon helpful (explizit/implizit): {{ }} %
- Stillstand-Eskalationen: {{ }}
- Spielregel-Overrides via Andre: {{ }}

## Empfehlungen fuer naechsten Run

### Fuer Blue-Team
{{ blue_recs }}

### Fuer Red-Team
{{ red_recs }}

### Fuer Lab-Setup
{{ lab_recs }}

### Fuer Hermes-GM-Skill
{{ skill_recs }}

## Action Items (Phase-2-Polish)

- [ ] {{ }}
- [ ] {{ }}
- [ ] {{ }}

## Anhang

- Wazuh-Alert-Dump: `lessons-learned/{{ run_date }}-wazuh-alerts.json`
- Telegram-Channel-Logs (pseudonymisiert): `lessons-learned/{{ run_date }}-chat-log.md`
- Snapshot-Archiv-Location: `s3://cyber-range-snapshots/{{ run_date }}/`
