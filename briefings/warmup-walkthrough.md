# Warm-up-Walkthrough — Cyber-Range Pilot

> **Für:** Andre (leitet das Warm-up)
> **Dauer:** 90 min, direkt nach dem Tear-up
> **Das ist dein Moderations-Skript.** Ziel: Am Ende sind alle im Lab-Tailnet, kennen die Map,
> haben ihre Tools einmal angefasst und wissen, in welchem Team sie sind.

---

## Vorab (während Tear-up, vor Ankunft der Spieler)

- [ ] `make lab-up` durchgelaufen, `make lab-status` grün
- [ ] `make preauth` → Pre-Auth-Keys für alle Teilnehmer + Co-GM generiert
- [ ] Onboarding-DM pro Person raus: individueller Pre-Auth-Key + Link zum Team-Briefing
      + Übungsvereinbarung
- [ ] Wazuh-Dashboard-Login + GM-Channel-Test-Ping geprüft
- [ ] Beamer/Screenshare bereit für den Lab-Map-Vortrag

---

## Block 1 — Tailnet-Onboarding (15 min)

**Ziel:** Jeder ist im Lab-Tailnet und kommt auf seine Workstation.

1. **Begrüßung + Übungsvereinbarung (3 min).** Kurz: Lab ist isoliert, freiwillig, jederzeit-Abbruch
   möglich, Logs werden nach dem Pilot gelöscht/anonymisiert. Wer noch nicht unterschrieben hat,
   macht das jetzt. *(Vollständiges Template: `docs/uebungsvereinbarung.md` — folgt separat.)*

2. **Tailscale installieren + einloggen (10 min).** Gemeinsam, Schritt für Schritt:
   ```bash
   # Tailscale-Client installieren (Linux-Beispiel; Win/Mac: App aus dem Store)
   curl -fsSL https://tailscale.com/install.sh | sh

   # Auf das LAB-Headscale zeigen (NICHT der normale Tailscale-Login!)
   sudo tailscale up --login-server https://<lab-headscale-public-ip>:443 --authkey <dein-key>

   # Prüfen:
   sudo tailscale status
   ```
   > ⚠️ **Häufiger Stolperstein:** Wer Tailscale schon privat nutzt, muss `--login-server`
   > explizit setzen, sonst landet er im falschen Tailnet. Geh rum und schau auf die Bildschirme.

3. **Verbindungstest (2 min).** Jeder pingt seine eigene Workstation:
   ```bash
   # Red:  ssh kali@kali-<dein-alias>
   # Blue: ssh ubuntu@blue-ws-<dein-alias>
   ```
   Klappt das bei allen? Dann weiter. Wer hängt, kriegt 1:1-Hilfe, der Rest macht Pause.

---

## Block 2 — Lab-Map-Vortrag (15 min)

**Ziel:** Alle haben dasselbe mentale Bild vom Lab. Am Beamer.

Zeig die Topologie und erklär die vier Subnetze:

```
DMZ   10.99.10.0/28   web-target / vault-target / linux-victim / nc-target   ← die 4 Ziele
RED   10.99.30.0/28   kali-*                                                 ← Angreifer-Workstations
BLUE  10.99.20.0/28   wazuh-siem / blue-ws-*                                 ← Verteidiger + SIEM
GM    10.99.40.0/28   hermes-gm / lab-headscale                              ← Spielleitung
```

Die `nc-target` (Nextcloud `:8090`) hält „Kundendaten" — Red will sie exfiltrieren, Blue ihre
Exfiltration erkennen (Data-Exfil-/DLP-Szenario).

Kernbotschaften:
- **Die Firewall trennt Red und Blue.** Red darf ins DMZ, nicht zu Blue. Blue darf ins DMZ
  (Forensik) + zum Wazuh-Dashboard. Niemand greift außerhalb des Labs an.
- **Drei Ziele, eine Kill-Chain.** Recon → Initial Access → Priv-Esc → Persistence → Lateral → Exfil.
  Red spielt sie, Blue erkennt sie.
- **Hermes-GM ist der KI-Spielleiter** in euren Telegram-Channels. Fragt ihn alles, er gibt Hints,
  keine Spoiler, nichts cross-team.
- **Es ist kein Krieg.** Zwei Perspektiven auf dasselbe Geschehen. Im Debrief tauscht ihr sie aus.

---

## Block 3 — Gemeinsamer Tool-Walkthrough (30 min)

**Ziel:** Jeder hat sein Haupt-Tool einmal live gesehen. Beide Teams zusammen — so versteht Red,
was Blue sieht, und umgekehrt.

1. **Red-Demo (12 min):** Auf `kali-andre` einen harmlosen Scan zeigen:
   ```bash
   nmap -sV web-target
   gobuster dir -u http://web-target:8080 -w /usr/share/wordlists/dirb/common.txt
   ```
   Erklär: „Das ist Recon. Jeder Scan hinterlässt Spuren."

2. **Blue-Demo (12 min):** Sofort danach im Wazuh-Dashboard zeigen, **dass genau dieser Scan
   gerade Alerts/Log-Einträge erzeugt hat.** Das ist der Aha-Moment: *Angriff erzeugt Telemetrie.*
   Zeig Triage, Filtern nach Source-IP, einen Alert aufklappen.

3. **Hermes-GM-Demo (6 min):** Stell live eine Frage im GM-Channel, z.B.
   *„Erklär mir die Pyramid of Pain"* — und zeig, wie gestufte Hints aussehen. Sag dazu: Stillstand
   >30 min → er meldet sich selbst.

> Das ist der pädagogische Kern des Tages: **Red macht Lärm, Blue hört ihn.** Wenn dieser
> Zusammenhang sitzt, hat das Warm-up sein Ziel erreicht.

---

## Block 4 — Getrennte Team-Briefings (30 min)

**Ziel:** Jedes Team geht in seine Rolle. Räumlich trennen (zwei Ecken/Räume).

- **Red** (mit Andre, ~15 min Fokus) → `red-team-briefing.md` durchgehen: Mission, Rules of
  Engagement, die 6 Phasen, Trophy-Ziel, Hermes-Channel. Klären: Wer übernimmt welchen
  Initial-Access-Pfad in Phase B?
- **Blue** (mit Co-GM, oder Andre wechselt rüber) → `blue-team-briefing.md` durchgehen: Mission
  (detect/investigate/document), Wazuh-Zugang, Lernziele L1–L4, der Threat-Hunting-Loop,
  PICERL. Klären: Wer macht Live-Triage, wer Forensik, wer Doku?
- Beide Teams legen **eine Baseline-Runde** ein: Red sieht sich die Targets an, Blue lernt das
  normale Dashboard-Bild kennen.

> Falls kein Co-GM mitmoderiert: Brief Red zuerst (15 min), gib ihnen eine konkrete „schaut euch
> Phase A an"-Aufgabe, dann wechsle zu Blue.

---

## Übergang in Runde 1

Wenn alle Teams gebrieft sind und die Tools laufen:
- Kurz alle zusammenholen: „Runde 1 ist Phase A–C, 2,5 Stunden. Hermes koordiniert, ich spiele
  bei Red mit. Bei Problemen → GM-Channel oder kommt zu mir."
- Startsignal geben. Hermes-GM ab jetzt im Push-Mode.

Los geht's. 🚀
