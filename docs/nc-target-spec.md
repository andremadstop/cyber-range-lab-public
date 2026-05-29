# NC-Target-Spec — Nextcloud als Data-Exfil-Ziel (Pilot, In-Scope)

> **Spec-ID:** CRL-NC-001 · **Datum:** 2026-05-28 · **Status:** Build-Auftrag an Hermes
> **Entscheidung:** NC ist 4. DMZ-Target im Mo/Di-Pilot (Andre, 2026-05-28).
> **Design-Prinzip für den Tonight-Build:** Robustheit > Exploit-Raffinesse. Schwache Credentials
> + Dummy-Daten + NC-Log-basierte Detection — KEINE fragile NC-CVE-Jagd, die beim Deploy kippt.
> **Out-of-Scope (Phase 2):** Comms-Compromise / OOB-Fallback-Mechanik. NUR das Exfil-Target bauen.

## 1. Infrastruktur (Terraform)

- **Host:** `nc-target`, Hetzner CX22, DMZ-Subnet, **`10.99.10.5`** (4. DMZ-Target → Lab jetzt **14 VMs**).
- Gleiche Cloud-Firewall-Klasse wie web/vault/linux-victim: `RED→DMZ allow`, `BLUE→DMZ tcp/22+icmp`,
  `DMZ→Internet allow`, **`RED→BLUE deny`** bleibt.
- Wazuh-Agent auf `nc-target` (analog 21-wazuh-agents.yml).

## 2. Software (Ansible-Rolle `nextcloud-victim`)

- Nextcloud via offizielles `docker-compose` (nextcloud + MariaDB + Redis).
- Erreichbar `10.99.10.5:8090 → :80` (Port-Schema analog web-target `:8080`).
- **Admin-Account schwaches PW** (Top-1000-Liste, z.B. wie vault-target). **PW NICHT committen** →
  `briefings/spieltag-zugaenge.local.md` (gitignored).
- Audit-/Logging-App aktiv, `nextcloud.log` (JSON) wird vom Wazuh-Agent eingelesen.

## 3. Dummy-Daten ("Kundendaten" — generiert, KEINE echten PII)

Seed-Script erzeugt im Admin-Files-Ordner `Kundendaten/`:
- `kundenliste.csv` (~50 Fake-Firmen + Fake-Ansprechpartner, via Faker)
- `vertraege/` (~10 Fake-Vertrags-PDFs/-TXTs)
- `rechnungen/` (~20 Fake-Rechnungen)
- `intern/passwoerter.xlsx` — **Honeypot-Köder** (Fake-Creds, einer davon „funktioniert" als
  Bridge zu `linux-victim` → Lateral-Movement-Verknüpfung mit bestehender Chain)
- `intern/FLAG-kundendaten.txt` — Trophy-Marker für Exfil-Erfolgskriterium

Alle Daten via `Faker`/`pwgen` generiert, idempotent, klar als Fake markiert.

## 4. Angriffspfad (Red) — slotet in bestehende Chain

- **Phase B (Initial Access):** NC-Admin-Login schwaches PW (Hydra gegen NC-Login) ODER
  über-permissiver Public-Share-Link. → Zugriff auf `Kundendaten/`.
- **Phase E (Lateral, optional):** Honeypot-Cred aus `passwoerter.xlsx` → SSH zu `linux-victim`.
- **Phase F (Exfiltration):** `Kundendaten/`-Set via WebDAV/HTTPS-Download rausziehen
  (`FLAG-kundendaten.txt` = Erfolgskriterium). Das ist das realistische DLP-Szenario.

## 5. Detection (Blue / Wazuh) — neue Custom-Rules

Anschluss an bestehendes Schema `100010–100080`, NC bekommt **`100090–100092`**:

| Rule | Lernziel | Trigger |
|---|---|---|
| `100090` | L1 | **NC-Brute-Force** (>10 Login-Versuche/60s) |
| `100091` | L2 | **NC-Exploit-Versuch** (Identity-Proof / Status-Abfrage) |
| `100092` | L4 | **NC-Massen-Exfiltration** (>20 Dateiabrufe/120s) |

> **Stand 2026-05-29:** so von Hermes gebaut (`22-wazuh-rules.yml` auf `main`). Ursprüngliche
> Spec sah 100092=Share-Creation vor — Hermes hat stattdessen Exploit-Detection umgesetzt; Brute
> und Exfil sind abgedeckt.

→ `docs/detection-rules.md` + `ansible/playbooks/22-wazuh-rules.yml` entsprechend ergänzen,
`docs/attack-chain.md` um den NC-Pfad erweitern (Phase B/F).

## 6. Akzeptanzkriterien

- `terraform plan` zeigt **14 VMs**.
- NC erreichbar, `Kundendaten/` mit Dummy-Daten vorhanden (idempotenter Seed).
- Rules `100090–100092` deployed, feuern im Smoke-Test (1× Mass-Download triggert `100090`).
- Keine Klartext-Credentials im Repo (alles im gitignored Handout).
- Lokaler Syntax-/Molecule-Check grün.
