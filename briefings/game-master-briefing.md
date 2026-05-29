# Game-Master-Briefing — Cyber-Range Pilot

> **Für:** Andre (Game-Master + Red-Lead) und den Co-GM
> **Spieltag:** Mo 2026-06-01 oder Di 2026-06-02
> **Das ist dein Operator-Briefing — der Blick hinter die Kulissen.**

---

## Dein Versprechen an dich selbst

Du willst am Spieltag **mitspielen** (Red-Lead), nicht die ganze Zeit Spielleitung machen.
Deshalb gibt es Hermes-GM: Er übernimmt die operative Spielleitung. Du behältst das **Override-Recht**
und greifst nur ein, wenn nötig. Das funktioniert nur, wenn du Hermes vor dem Spieltag einmal
verstanden hast — dafür ist dieses Briefing.

Falls ein Co-GM dabei ist: Ihr teilt euch die menschliche
Aufsicht. Er beobachtet beide Teams neutral, du bist gleichzeitig Red-Lead. Falls der Co-GM
stattdessen aktiv als Blue-Lead mitspielt (Fallback), trägst du die GM-Aufsicht allein — dann
umso wichtiger, dass Hermes rund läuft.

---

## Run-of-Show (8h-Spieltag)

| Block | Dauer | Wer leitet | Inhalt |
|---|---|---|---|
| Tear-up | 30 min | Andre | `make lab-up`, Pre-Auth-Keys, Onboarding-Mails |
| Warm-up | 90 min | Andre | Tailnet-Onboarding, Lab-Map, Tool-Walkthrough, Team-Briefings (→ `warmup-walkthrough.md`) |
| Runde 1 | 2.5 h | Hermes-GM koordiniert | Phase A–C (Recon, Initial Access, Priv-Esc) |
| Zwischenanalyse | 30 min | Andre + Co-GM | Snapshot, Hints, ggf. Eskalation |
| Runde 2 | 2.5 h | Hermes-GM koordiniert | Phase D–F (Persistence, Lateral, Exfil) |
| Debrief | 1 h | Andre + Co-GM | Hermes-Auto-Report, gemeinsame Lessons Learned |

Während Runde 1 und 2 bist du primär Red-Lead. Halte nebenher ein Auge auf den GM-Channel.

---

## Wie Hermes-GM funktioniert (dein mentales Modell)

Hermes läuft auf einer eigenen VM (`hermes-gm`, `10.99.40.2`) und arbeitet in **vier Modi**:

1. **Pull-Mode** — beide Teams haben einen Telegram-Channel (`cyber-range-red`, `cyber-range-blue`)
   und fragen Hermes aktiv. Er antwortet team-spezifisch, mit gestuften Hints, **nie cross-team**.
2. **Push-Mode** — er pollt Wazuh alle 2 min. Erkennt er **Stillstand** (>30 min keine neue
   Aktivität in einem Team), schickt er einen ungefragten Hint. Feuert eine lernziel-relevante
   Rule, pingt er Blue („findet ihr den Alert?").
3. **Honcho-Profile** — er führt pro Spieler ein (pseudonymisiertes) Skill-Profil und kalibriert
   die Hint-Tiefe: Anfänger kriegen mehr Kontext, Fortgeschrittene sokratische Gegenfragen.
4. **Auto-Report** — am Ende generiert er den Lessons-Learned-Report (MITRE-Heatmap,
   Rule-Trigger-Statistik, „Was hat Blue verpasst").

**Der GM-Channel `cyber-range-gm` sieht alles** — beide Team-Channels, alle Hints, alle Alerts.
Das ist dein Cockpit.

---

## Steuerung — was Hermes WIRKLICH kann (Stand B6-Build)

> ⚠️ **Reality-Check:** Der gebaute `telegram_router.py` (Phase B6) implementiert **noch keine**
> `/override`-Slash-Befehle. Frühere Briefing-Entwürfe haben solche Befehle erfunden — die gibt es
> im Code nicht. Hier steht, was die Skill-Version tatsächlich tut:

**Hermes-GM (gebaut):**
- **Channel-Routing:** beantwortet Fragen in `cyber-range-red` / `cyber-range-blue`, CC an `cyber-range-gm`.
- **Auto-Hints:** gestufte Tiefe (Level 1 = richtungsweisend ohne Commands, Level 2 = konkreter
  Command + Ausgabe-Erwartung). Policy aus `gm_context.yaml`: **max. 6 Hints/Stunde pro Spieler**,
  proaktiver Hint bei **Stillstand > 120 min**.
- **GM-Channel** sieht alles mit.

**Manuelle GM-Kontrolle (bis ein Override-Handler nachgebaut ist):**
- **Steuern über Sprache:** Du/Co-GM redet direkt mit den Teams im Raum — das ist euer primärer Hebel.
- **Hermes stoppen/neustarten** (Notbremse), siehe Runbook unten.
- **Vor dem Spieltag entscheiden:** Reicht „GM steuert verbal + Auto-Hints", oder soll Hermes vorher
  einen echten `/override`-Befehlssatz bekommen (mute/force-hint/difficulty)? Das ist ein kleines
  Skill-Update — als Aufgabe an die Build-Session, **nicht** am Spieltag improvisieren.

**Faustregel:** Greif **so wenig wie möglich** ein. Hermes regelt Hints selbst. Dein Mehrwert als
Mensch ist genau das, was die KI *nicht* kann — Stimmung lesen, Lehr-Momente setzen, Konflikte lösen.

---

## Wann DU als Mensch eingreifst (nicht Hermes)

- **Technischer Defekt:** Eine VM hängt, Wazuh-Dashboard down → Operator-Eingriff (siehe unten).
- **Stimmung kippt:** Jemand ist abgehängt oder genervt → menschliches Gespräch, nicht KI-Hint.
- **Sicherheits-/Spielregel-Verstoß:** Jemand probiert das RED→BLUE-Verbot oder greift was außerhalb
  des Labs an → sofort stoppen, ansprechen.
- **Lehr-Moment:** Etwas Spannendes passiert (eine elegante Detection, ein cleverer Exploit) →
  kurz alle zusammenholen und zeigen. Das ist der Mehrwert eines menschlichen GM.

---

## Operator-Cheatsheet (Lab-Steuerung)

```bash
cd ~/Workspace/Code/cyber-range-lab

make lab-up         # Lab hochfahren (~10 min)
make lab-status     # Health-Check: alle Hosts up? Wazuh-Baseline? Hermes responsive?
make preauth        # Pre-Auth-Keys für alle Teilnehmer generieren
make lab-snapshot   # Phase-Snapshot (z.B. vor Zwischenanalyse — Replay-Option)
make lab-down       # Tear-down + Snapshot-Archiv (am Spielende!)
```

- **Lab-Umfang:** 14 VMs — 4 DMZ-Targets (`web-target`, `vault-target`, `linux-victim`,
  **`nc-target`** = Nextcloud-Data-Exfil-Ziel), Wazuh, 4 Kali, 3 Blue, hermes-gm, lab-headscale.
- **Vor Spielstart:** `make lab-status` muss grün sein — alle Hosts up, Baseline-Traffic läuft,
  NC mit Dummy-Kundendaten erreichbar, Hermes-GM antwortet auf einen Test-Ping im GM-Channel.
- **Zwischenanalyse:** Erst `make lab-snapshot`, dann Hints/Eskalation. So hast du einen
  Wiederherstellungspunkt, falls in Runde 2 etwas schiefgeht.
- **Kosten:** Das Lab kostet ~5 € für den ganzen Tag. **`make lab-down` nicht vergessen** — sonst
  läuft die Uhr weiter (~60 €/Monat bei Dauerbetrieb). Hard-Stop liegt bei 50 €.

---

## Wenn etwas schiefgeht (kurze Triage)

| Symptom | Erster Check |
|---|---|
| VM nicht erreichbar | `make lab-status`, Hetzner-Console → VM-Status |
| Wazuh-Dashboard leer | Baseline-Traffic-Generator läuft? Agents connected? |
| Hermes-GM antwortet nicht | `hermes-gm`-VM up? LLM-Cost-Cap (5 €/Iteration) erreicht? |
| Spieler kommt nicht ins Tailnet | Pre-Auth-Key abgelaufen (72h)? Neuen via `make preauth` |
| Ein Team rast/steckt | `/override difficulty up`/`down`, oder manueller Hint |

Im Zweifel: **Snapshot ziehen, dann reparieren.** Lieber 5 min Pause als ein verlorener Spieltag.

---

## Nach dem Spiel

1. `/report` → Hermes generiert den Lessons-Learned-Report (`lessons-learned/2026-06-0X-pilot.md`).
2. Gemeinsamer Debrief: Report durchgehen, Red zeigt ihre Sicht, Blue ihre. Was wurde erkannt,
   was verpasst, warum?
3. `make lab-down` — Tear-down, Snapshots wandern ins Object-Storage-Archiv.
4. Deine menschliche Ergänzung zum Report (das, was Hermes nicht sieht): Stimmung, Co-GM-Feedback,
   was du fürs nächste Mal anders machen würdest.

Viel Erfolg. Du hast das Lab gebaut — heute spielst du drin. 🎮
