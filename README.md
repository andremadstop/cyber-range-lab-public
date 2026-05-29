# Cyber-Range Lab

> ⚠️ **Öffentliche, bereinigte Kopie.** Alle Credentials sind Platzhalter (`CHANGEME_*`) — setze
> deine eigenen (idealerweise via Secrets-Manager/Ansible-Vault). Interne Infrastruktur-Referenzen,
> Klarnamen und Geschäftsdaten wurden entfernt. Diese Kopie dient zum Teilen/Übernehmen des Projekts.

> Wochenend-Cyber-Range fuer Red-Team vs. Blue-Team Trainings.
> Production-ready IaC, KI-Spielleitung via Hermes.

## Status

- **Phase**: Pilot 0.1 (Setup-Sprint)
- **Format**: Live-Run mit CySA+-Kursteilnehmern
- **Rollen**: Game-Master (Mensch) + Hermes-GM (KI-Co-Spielleiter)

## Was das hier ist

Ein vollstaendig automatisiertes Trainings-Lab fuer Cybersecurity-Uebungen:

- 13 isolierte Hetzner-Cloud-VMs (DMZ-Targets, Wazuh-SIEM, Workstations Red+Blue, Hermes-GM)
- Eigenes Headscale-Mesh (separates Tailnet, hart isoliert)
- One-Command Tear-up / Tear-down via Terraform + Ansible
- 6-Phasen-Attack-Chain mit Detection-Rule-First-Design
- KI-Spielleiter (Hermes-Agent) der proaktiv Hinweise gibt, Stillstand erkennt,
  Spielerprofile via Honcho mitfuehrt und Auto-Lessons-Learned-Report generiert

## Quickstart

```bash
# Voraussetzungen siehe docs/setup.md
make lab-up        # Lab hochfahren (~10 min)
make lab-status    # Health-Check
make lab-snapshot  # Phase-Snapshot fuer Replay
make lab-down      # Cleanup + Snapshot-Archiv
```

## Repo-Struktur

```
.
├── docs/                 # Architektur, Attack-Chain, Detection-Rules, Runbooks
├── briefings/            # Red/Blue/GM/Warmup-Briefings als Markdown
├── terraform/            # Hetzner-Infra-as-Code
├── ansible/              # Configuration-Management aller VMs
├── scripts/              # lab-up/down/snapshot/status
├── hermes-gm-skill/      # Hermes-Skill fuer KI-Spielleitung (Voll-Variante)
├── lessons-learned/      # Auswertungs-Reports pro Run
└── Makefile              # Top-Level-Targets
```

## Lizenz

**AGPL-3.0** fuer Community/private Nutzung. Kommerzielle Lizenz auf Anfrage.

## Beitragende

- Andre — Konzept, Spielleitung
- Claude (Anthropic) — Architektur + Specs
- Hermes (NousResearch) — Implementation (Multi-KI-Workflow)
