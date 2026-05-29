# Cyber-Range GM — KI-Spielleiter Setup

## Voraussetzungen

- Python >= 3.11
- Telegram-Bot (erstellt via @BotFather)
- Zugriff auf Wazuh-API (Port 55000)
- Honcho-Instanz (optional, Stateless-Fallback vorhanden)
- LLM-API-Key (Gemini oder DeepSeek)

## Installation

```bash
cd hermes-gm-skill
pip install -r requirements.txt
```

## Konfiguration

Umgebungsvariablen oder `config.yaml`:

```yaml
# config.yaml
telegram:
  bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
  channels:
    red: "-1001234567890"
    blue: "-1001234567891"
    gm: "-1001234567892"

wazuh:
  base_url: "https://10.99.20.2"
  username: "admin"
  password: "CHANGEME_set_in_your_vault"

honcho:
  base_url: "http://localhost:8080"
  api_key: ""
  app_name: "cyber-range-coach"

llm:
  provider: "gemini"  # oder "deepseek"
  api_key: "YOUR_API_KEY"
  model: "gemini-2.5-flash"

gm_context: "gm_context.yaml"
```

## Module Uebersicht

| Modul | Beschreibung |
|-------|-------------|
| `wazuh_poller` | Pollt Wazuh-API alle 2min, Alert-Erkennung |
| `telegram_router` | 3 Channels (red/blue/gm), Safety-Filter |
| `honcho_client` | Spielerprofile lesen/schreiben |
| `hint_policy` | Stillstand-Erkennung, adaptive Hint-Tiefe |
| `report_generator` | Lessons-Learned-Report via LLM |
| `llm_provider` | Gemini/DeepSeek-Adapter |
| `safety_filter` | Token-Leak-Praevention (Pflicht!) |

## Tests

```bash
cd hermes-gm-skill
pip install -e ".[dev]"
pytest tests/ -v --cov=modules
```

## Betrieb

### Push-Mode (proaktiv)

Der Poll-Loop laeuft alle 2 Minuten:
1. Wazuh-API: neue Alerts abrufen
2. Stillstand-Erkennung (>30 min)
3. Bei Bedarf: proaktiven Hint senden

### Pull-Mode (reaktiv)

Spieler fragen via Telegram:
1. Nachricht in Red/Blue-Channel
2. Router identifiziert Team
3. Honcho-Profil laden
4. Hint-Tiefe bestimmen
5. LLM generiert Antwort
6. Safety-Filter vor Outbound

### Report-Generierung

Nach Spielende via `/report`:
1. Alle Alerts aus Wazuh abrufen
2. Telegram-History parsen
3. Honcho-Insights einlesen
4. LLM generiert Report
5. Speicherung + Telegram-Post

## Fehlerbehandlung

- **Wazuh offline**: Poller gibt leere Listen, kein Spielabbruch
- **Honcho offline**: Stateless-Mode (Default-Profile)
- **LLM-API-Fehler**: Fallback auf Template-basierte Antworten
- **Telegram-API-Fehler**: Retry mit Exponential-Backoff

## Sicherheit

- `safety_filter.py` MUSS vor jedem Outbound aufgerufen werden
- Keine Tokens in Logs oder Reports
- Honcho-Profile pseudonymisiert (keine Klarnamen)
- GM-Channel hat Voll-Einblick + Override-Befehle
