# Setup & Operator-Guide

> **Spec-ID:** CRL-SETUP-001
> **Für:** André (Operator). Technisches Runbook fürs Hochfahren, Betreiben und Abbauen des Labs.
> **Begleitend:** `briefings/game-master-briefing.md` (Spielleitung), `architecture.md` (Spec).

---

## 0. Voraussetzungen

**Lokal auf der Operator-Workstation:**

| Tool | Version | Wofür |
|---|---|---|
| Terraform | ≥ 1.7 | Hetzner-Infra |
| Ansible-core | ≥ 2.16 | VM-Konfiguration |
| Python | ≥ 3.11 | Hermes-GM-Skill, Skripte |
| `hcloud` CLI | aktuell | Hetzner-Inspektion |
| Tailscale-Client | aktuell | Lab-Tailnet-Zugang |
| `git`, `make`, `jq` | — | Lifecycle |

**Accounts / Secrets** (alle in Vaultwarden, **nie** im Repo):

- Hetzner-API-Token (Item: `Hetzner API cyber-range-lab (hermes-builder)`) — Scope: Projekt
  `cyber-range-lab`, read+write.
- Budget-Cap im Hetzner-Projekt: **Alert bei 25 €, Hard-Stop bei 50 €**.
- SSH-Key (`~/.ssh/id_ed25519` o.ä.) im Hetzner-Projekt hinterlegt.

---

## 1. Erstkonfiguration (einmalig pro Run)

```bash
cd ~/Workspace/Code/cyber-range-lab/terraform

# tfvars aus Template
cp terraform.tfvars.example terraform.tfvars
chmod 600 terraform.tfvars
# editieren: hcloud_token = "<aus Vaultwarden>"

# SSH-Keys der Teilnehmer (gitignored!)
cat > ssh-keys.local.yml <<'EOF'
keys:
  andre: <dein-public-key>
  # Mitschüler-Keys im Onboarding ergänzen
EOF
chmod 600 ssh-keys.local.yml

# Teilnehmer-Aliase (gitignored, Klarnamen nur lokal)
cp participants.local.yml.example participants.local.yml
# editieren mit echten Aliasen + Skill-Levels
```

> ⚠️ `terraform.tfvars`, `ssh-keys.local.yml`, `participants.local.yml` sind **gitignored**.
> Niemals committen — sie enthalten Token, Keys oder Klarnamen.

**Plan-Check vor dem ersten echten Apply:**
```bash
terraform init
terraform validate
terraform plan -out=plan.bin 2>&1 | tee plan.log
grep -c "will be created" plan.log   # Erwartet: 12 (oder 13 bei Co-GM-Blue-Lead-Fallback)
```

---

## 2. Lab-Lifecycle (`make`-Targets)

```bash
make help          # Übersicht aller Targets

make lab-up        # terraform apply + Ansible-Runs (~10 min)
make lab-status    # Health-Check: alle Hosts up? Wazuh-Baseline? Hermes responsive?
make preauth       # Pre-Auth-Keys für alle Workstations generieren
make lab-snapshot  # manueller Phase-Snapshot (Replay-Punkt)
make lab-restore   # Restore vom letzten Snapshot
make lab-down      # Teardown + finaler Snapshot ins Object Storage
make keys-rotate   # SSH-Keys + Vault-Master-PW rotieren
make test          # pytest (Hermes-GM-Skill) + Ansible-Syntax-Check
make lint          # terraform fmt + ansible-lint + yamllint
make clean         # lokale Artefakte löschen (KEIN Hetzner-Teardown!)
```

> **`make clean` ≠ `make lab-down`.** `clean` räumt nur lokale Dateien auf; die Hetzner-VMs
> laufen weiter (= Kosten). Für echten Teardown immer `make lab-down`.

---

## 3. Spieltag-Ablauf (Operator-Sicht)

1. **Morgens — Tear-up:**
   ```bash
   make lab-up && make lab-status
   make preauth          # Keys für alle Teilnehmer + Co-GM
   ```
   `make lab-status` muss **grün** sein: alle Hosts up, Baseline-Traffic läuft (~100 Events/min),
   Hermes-GM antwortet auf Test-Ping im GM-Channel.

2. **Onboarding-DMs raus** — pro Person: individueller Pre-Auth-Key + Link zu
   `docs/spieler-onboarding.md` + Übungsvereinbarung-PDF.

3. **Warm-up** — folge `briefings/warmup-walkthrough.md` (90 min).

4. **Vor der Zwischenanalyse:** `make lab-snapshot` (Replay-Punkt, falls Runde 2 schiefgeht).

5. **Debrief:** `/report` im GM-Channel → Hermes generiert
   `lessons-learned/2026-06-0X-pilot.md`.

6. **Abends — Teardown:**
   ```bash
   make lab-down
   ```
   Erwartet: alle VMs destroyed, Snapshots im Object-Storage-Archiv. **Nicht vergessen** —
   sonst laufen die Kosten weiter (~60 €/Monat bei Dauerbetrieb).

---

## 4. Tailnet-Zugang (Operator)

Das Lab nutzt ein **eigenes Headscale**, getrennt vom normalen Tailnet:

```bash
# Public-IP aus Terraform-Output
HEADSCALE_IP=$(cd terraform && terraform output -raw lab_headscale_public_ip)

# Ins Lab-Tailnet (Operator-Key)
sudo tailscale up --login-server https://${HEADSCALE_IP} --authkey <andre-key>
sudo tailscale status   # alle Lab-Hosts sichtbar?

# Headscale-Health
ssh root@${HEADSCALE_IP} 'systemctl status headscale | head -5'
ssh root@${HEADSCALE_IP} 'headscale policy check'   # ACL valid?

# Zurück ins normale Tailnet
sudo tailscale logout && sudo tailscale up
```

---

## 5. Troubleshooting

| Symptom | Erster Check |
|---|---|
| VM nicht erreichbar | `make lab-status`, Hetzner-Console → VM-Status |
| Wazuh-Dashboard leer | Baseline-Traffic-Generator? Agents connected? |
| Hermes-GM stumm | `hermes-gm`-VM up? LLM-Cost-Cap (5 €/Iteration) erreicht? |
| Spieler kommt nicht ins Tailnet | Pre-Auth-Key abgelaufen (72h)? → `make preauth` |
| Apply schlägt fehl | `terraform plan` erneut, Token-Scope + Budget-Cap prüfen |

**Goldene Regel bei Problemen:** erst `make lab-snapshot`, dann reparieren. Lieber 5 min Pause
als ein verlorener Spieltag.

---

## 6. Kosten & Sicherheit (Kurzfassung)

- **~5 €** für einen kompletten 48h-Spieltag. Hard-Stop bei 50 € im Hetzner-Projekt.
- Lab-Tailnet ist eine **separate Headscale-Instanz**, keine Bridge zum Homelab-Tailnet.
- Pre-Auth-Keys: ephemeral-Verhalten, **72h Expiry**, nicht reusable.
- Hermes-`safety_filter.py` redacted Tokens in allen Outbound-Messages — trotzdem: **nie**
  Secrets in Telegram/Logs posten.
- DMZ→Internet ist offen (Reverse-Shell für Phase F). Für air-gapped-Runs via Cloud-Firewall schließbar.

## Referenzen

- `docs/architecture.md` — vollständige Spec
- `docs/attack-chain.md` — 6-Phasen-Detail + Detection-Mapping
- `briefings/game-master-briefing.md` — Spielleitung + Override-Befehle
- Wazuh Docs: https://documentation.wazuh.com/
