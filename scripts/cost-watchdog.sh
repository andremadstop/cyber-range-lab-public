#!/usr/bin/env bash
# Cost-Watchdog für Hetzner Cyber-Range Lab
#
# Hetzner Cloud API hat KEINEN Billing-Endpoint und KEINEN Hard-Stop bei Budget-Ueberschreitung.
# Dieses Script ist der selbstgebaute Ersatz:
#   - Listet alle laufenden Server im Projekt
#   - Berechnet projected monthly cost (730h-Modell)
#   - Schickt Telegram-Alert bei ALERT_THRESHOLD_EUR
#   - Triggert terraform destroy bei HARD_STOP_EUR
#
# Designed for: cron/systemd-timer, alle 30 min.
#
# Voraussetzungen:
#   - HCLOUD_TOKEN in ENV oder .env.local
#   - hcloud CLI installiert
#   - TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in ENV (optional, sonst nur stderr)
#   - terraform CLI fuer Hard-Stop-Action

set -euo pipefail

# ─── Konfiguration ─────────────────────────────────────────────────────────────

ALERT_THRESHOLD_EUR="${ALERT_THRESHOLD_EUR:-25}"
HARD_STOP_EUR="${HARD_STOP_EUR:-50}"
PROJECT_NAME="cyber-range-lab"
TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/terraform"
LOG_FILE="${LOG_FILE:-/tmp/cost-watchdog.log}"

# Hetzner CX/CCX hourly rates (Stand Mai 2026, vor 15. Juni Preisaenderung)
# Format: SERVER_TYPE_EUR_PER_HOUR
declare -A HOURLY_RATES=(
  [cx22]="0.007"
  [cx32]="0.013"
  [cx42]="0.027"
  [cx52]="0.057"
  [ccx13]="0.020"
  [ccx23]="0.040"
  [cax11]="0.005"
  [cax21]="0.010"
)

# ─── ENV-Loading ───────────────────────────────────────────────────────────────

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$REPO_ROOT/.env.local" ]; then
  # shellcheck disable=SC1090
  set -a; source "$REPO_ROOT/.env.local"; set +a
fi

if [ -z "${HCLOUD_TOKEN:-}" ]; then
  echo "FEHLER: HCLOUD_TOKEN nicht gesetzt (env oder .env.local)" >&2
  exit 1
fi

# ─── Helpers ───────────────────────────────────────────────────────────────────

log() {
  local msg="[$(date -Iseconds)] $*"
  echo "$msg" | tee -a "$LOG_FILE" >&2
}

telegram_notify() {
  local msg="$1"
  if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    log "Telegram nicht konfiguriert, ueberspringe Notification: $msg"
    return 0
  fi
  curl -s --max-time 10 \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=$msg" \
    -d "parse_mode=Markdown" > /dev/null || log "WARN: Telegram-Send fehlgeschlagen"
}

# ─── Hauptlogik ────────────────────────────────────────────────────────────────

main() {
  log "Cost-Watchdog start, project=$PROJECT_NAME, alert=${ALERT_THRESHOLD_EUR}EUR, hard-stop=${HARD_STOP_EUR}EUR"

  # Server-Liste holen (JSON)
  local servers_json
  servers_json=$(hcloud server list -o json 2>&1) || {
    log "FEHLER: hcloud server list failed: $servers_json"
    telegram_notify "🔴 *Cost-Watchdog FEHLER:* Hetzner-API nicht erreichbar oder Token invalid"
    exit 1
  }

  local server_count
  server_count=$(echo "$servers_json" | jq '. | length')
  log "Server gefunden: $server_count"

  if [ "$server_count" -eq 0 ]; then
    log "Keine Server laufen, nichts zu tun"
    exit 0
  fi

  # Aktuelle stuendliche Kosten berechnen
  local total_hourly=0
  while IFS= read -r entry; do
    local stype name
    stype=$(echo "$entry" | jq -r '.server_type.name')
    name=$(echo "$entry" | jq -r '.name')
    local rate="${HOURLY_RATES[$stype]:-0.000}"
    if [ "$rate" = "0.000" ]; then
      log "WARN: Unbekannter Server-Typ '$stype' fuer Server '$name', skip"
      continue
    fi
    total_hourly=$(echo "$total_hourly + $rate" | bc -l)
    log "  - $name ($stype): ${rate} EUR/h"
  done < <(echo "$servers_json" | jq -c '.[]')

  # Projected monthly cost (730h/Monat = Hetzner-Modell)
  local projected_monthly
  projected_monthly=$(echo "$total_hourly * 730" | bc -l)
  projected_monthly=$(printf "%.2f" "$projected_monthly")

  log "Hourly: $total_hourly EUR | Projected monthly: $projected_monthly EUR"

  # Aktionen
  local stop_threshold_reached=0
  if (( $(echo "$projected_monthly > $HARD_STOP_EUR" | bc -l) )); then
    log "🔴 HARD-STOP ueberschritten ($projected_monthly > $HARD_STOP_EUR EUR)"
    telegram_notify "🔴 *HARD-STOP:* Projected $projected_monthly EUR/Mo (Limit: $HARD_STOP_EUR). Triggere \`terraform destroy\`."
    stop_threshold_reached=1
  elif (( $(echo "$projected_monthly > $ALERT_THRESHOLD_EUR" | bc -l) )); then
    log "🟡 ALERT ueberschritten ($projected_monthly > $ALERT_THRESHOLD_EUR EUR)"
    telegram_notify "🟡 *Cost-Alert Cyber-Range:* Projected $projected_monthly EUR/Mo ($server_count Server laufen). Limit: $HARD_STOP_EUR EUR."
  else
    log "✓ Im Budget ($projected_monthly < $ALERT_THRESHOLD_EUR EUR)"
  fi

  # Hard-Stop: terraform destroy
  if [ "$stop_threshold_reached" = "1" ]; then
    if [ ! -d "$TERRAFORM_DIR" ]; then
      log "FEHLER: $TERRAFORM_DIR nicht vorhanden, kann nicht destroyen"
      telegram_notify "🔴 *Hard-Stop FEHLGESCHLAGEN:* terraform-dir nicht gefunden, MANUELL handeln!"
      exit 2
    fi
    log "Starte terraform destroy in $TERRAFORM_DIR"
    if (cd "$TERRAFORM_DIR" && terraform destroy -auto-approve 2>&1 | tee -a "$LOG_FILE"); then
      telegram_notify "✅ *Hard-Stop ausgefuehrt:* Lab destroyed. Cost gesichert."
      log "terraform destroy erfolgreich"
    else
      telegram_notify "🔴 *terraform destroy FEHLGESCHLAGEN!* MANUELL pruefen!"
      log "FEHLER: terraform destroy failed"
      exit 3
    fi
  fi
}

main "$@"
