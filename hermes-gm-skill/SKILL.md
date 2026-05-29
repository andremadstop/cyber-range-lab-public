---
name: cyber-range-gm
description: KI-Spielleiter fuer das Cyber-Range-Lab. Pull-Mode (Spieler-Fragen) + Push-Mode (proaktive Hints) + Auto-Report. Nutzt Wazuh-API + Honcho-Profile + Telegram-Bot.
category: devops
version: 0.1.0
pilot: 2026-06-01
author: Hermes Co-Builder (Andre / Beispiel GmbH)
---

# Cyber-Range GM — KI-Spielleiter

Hermes-Skill, der als neutraler KI-Spielleiter fuer Red-vs-Blue-Team-Uebungen fungiert.

## Channels

| Channel | Audience | Zweck |
|---------|----------|-------|
| `cyber-range-red` | Red-Team (4 Spieler) | Angriffs-Tipps, Tool-Fragen, CySA+-Konzepte |
| `cyber-range-blue` | Blue-Team (3 Spieler) | Detection-Tipps, Wazuh-Queries, Forensik-Hilfe |
| `cyber-range-gm` | Andre (Game-Master) | Voll-Einblick + Override-Befehle |

## Module

| Modul | Zweck |
|-------|-------|
| `wazuh_poller.py` | Pollt Wazuh-API alle 2 min, erkennt neue Alerts + Stillstand |
| `telegram_router.py` | 3-Channel-Routing mit team-spezifischen Kontext |
| `honcho_client.py` | Spielerprofile lesen/schreiben (Skill-Level, Fortschritt) |
| `hint_policy.py` | Stillstand-Erkennung + adaptive Hint-Tiefe |
| `report_generator.py` | Lessons-Learned-Report nach Spielende |
| `llm_provider.py` | Gemini/Codestral-Adapter |
| `safety_filter.py` | Token-Leak-Praevention (API-Keys, JWTs, SSH-Keys) |

## Quick-Start

```bash
# Abhaengigkeiten
pip install -r requirements.txt

# Konfiguration: config.yaml (siehe README)
cp config.yaml.example config.yaml

# Tests
pytest tests/ -v

# Run
python -m hermes_gm_skill
```

## Externe Abhaengigkeiten

- Wazuh 4.7 API (REST + JWT)
- Honcho gRPC (einem internen Host)
- Telegram Bot API
- Gemini/DeepSeek API (LLM-Inference)
- Hetzner Cloud API (VM-Health)
