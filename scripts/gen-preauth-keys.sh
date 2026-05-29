#!/usr/bin/env bash
# gen-preauth-keys.sh — Erzeugt Headscale-Pre-Auth-Keys fuer Lab-Teilnehmer
# Verwendung:
#   gen-preauth-keys.sh [--expiry 72h] [--reusable false] [--user player]
#
# Standard:
#   --expiry  72h  (3 Tage, passt zum Wochenend-Format)
#   --reusable false (einmaliger Gebrauch — Key invalid nach erstem Connect)
#   --user    wird abgefragt falls nicht angegeben
#
# Pre-Auth-Keys werden in /var/lib/headscale/preauth-keys/ gespeichert
# zur spaeteren Referenz (Spieler-Onboarding).

set -euo pipefail

# Pfade
HEADSCALE_CLI="/usr/bin/headscale"
HEADSCALE_CONFIG="/etc/headscale/config.yaml"
KEY_DIR="/var/lib/headscale/preauth-keys"
LOG_FILE="/var/log/headscale-preauth.log"

# Defaults
EXPIRY="72h"
REUSABLE=false
USER_NAME=""

# Argumente parsen
while [[ $# -gt 0 ]]; do
  case "$1" in
    --expiry)
      EXPIRY="$2"
      shift 2
      ;;
    --reusable)
      REUSABLE="$2"
      shift 2
      ;;
    --user)
      USER_NAME="$2"
      shift 2
      ;;
    --help|-h)
      echo "Verwendung: $0 [--expiry 72h] [--reusable false] [--user player]"
      exit 0
      ;;
    *)
      echo "Unbekanntes Argument: $1"
      exit 1
      ;;
  esac
done

# Pruefungen
if [[ ! -x "$HEADSCALE_CLI" ]]; then
  echo "[ERROR] Headscale-CLI nicht gefunden: $HEADSCALE_CLI" >&2
  exit 1
fi

if [[ ! -d "$KEY_DIR" ]]; then
  mkdir -p "$KEY_DIR"
fi

# User ermitteln
if [[ -z "$USER_NAME" ]]; then
  # Falls kein User angegeben: Liste existierender User zeigen
  echo "Verfuegbare Headscale-User:"
  $HEADSCALE_CLI user list 2>/dev/null || echo "(noch keine User angelegt)"
  echo ""
  read -r -p "Headscale-User (default: 'player'): " USER_NAME_INPUT
  USER_NAME="${USER_NAME_INPUT:-player}"
fi

# Key generieren
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
KEY_FILE="${KEY_DIR}/preauth-${USER_NAME}-${TIMESTAMP}.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generiere Pre-Auth-Key fuer User '${USER_NAME}'..." | tee -a "$LOG_FILE"

REUSABLE_FLAG=""
if [[ "$REUSABLE" == "false" ]]; then
  REUSABLE_FLAG="--reusable=false"
fi

# Key via Headscale-CLI erzeugen
if KEY_OUTPUT=$($HEADSCALE_CLI preauthkey create \
  --user "$USER_NAME" \
  --expiration "$EXPIRY" \
  $REUSABLE_FLAG 2>&1); then

  # Key aus Output extrahieren (Format: "Key: <key-string>")
  PREAUTH_KEY=$(echo "$KEY_OUTPUT" | grep -oP 'Key:\s*\K\S+' || echo "$KEY_OUTPUT")

  # In Datei schreiben
  {
    echo "# Pre-Auth-Key fuer User: ${USER_NAME}"
    echo "# Erzeugt: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# Ablauf: ${EXPIRY}"
    echo "# Reusable: ${REUSABLE}"
    echo "${PREAUTH_KEY}"
  } > "$KEY_FILE"

  chmod 600 "$KEY_FILE"

  echo "[OK] Key gespeichert in: ${KEY_FILE}"
  echo "[OK] Key: ${PREAUTH_KEY}"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Key generiert: ${PREAUTH_KEY}" >> "$LOG_FILE"

  # Ausgabe fuer Script-Consumer
  echo "PREAUTH_KEY=${PREAUTH_KEY}"
  echo "KEY_FILE=${KEY_FILE}"
else
  echo "[ERROR] Key-Generierung fehlgeschlagen: ${KEY_OUTPUT}" >&2
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: ${KEY_OUTPUT}" >> "$LOG_FILE"
  exit 1
fi
