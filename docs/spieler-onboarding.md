# Spieler-Onboarding — Cyber-Range Pilot

> **Für:** alle Teilnehmer:innen (Red + Blue)
> **Diese Anleitung bekommst du vorab als PDF/Talk-Link.** Sie bringt dich in ~15 Minuten ins Lab.
> **Fachbegriffe** bleiben Englisch (CySA+-Konvention).

---

## Was du mitbringst

- **Eigener Laptop** (Linux, macOS oder Windows) mit Adminrechten zum Installieren von Tailscale.
- Ein **Telegram-Konto** (für den Team-Channel mit dem KI-Spielleiter).
- Die unterschriebene **Übungsvereinbarung** (`uebungsvereinbarung.md`).
- Deinen **persönlichen Pre-Auth-Key** und deinen **Alias** — bekommst du per Talk-DM von André.

> Du brauchst **nichts** vorzubereiten oder zu lernen. Alle Tools laufen fertig auf deiner
> Lab-Workstation. Dein Laptop ist nur das Fenster ins Lab.

---

## Schritt 1 — Tailscale installieren

Das Lab läuft in einem eigenen, isolierten Mesh-Netzwerk (Tailnet, betrieben über Headscale).
Du verbindest dich mit einem Tailscale-Client.

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**macOS / Windows:** Tailscale aus dem App Store bzw. von https://tailscale.com/download installieren.

> 📷 *[Screenshot-Platzhalter: Tailscale-Installations-Dialog — wird vor dem Spieltag ergänzt /
> Loom-Video folgt in Phase 2]*

---

## Schritt 2 — Ins Lab-Tailnet einloggen

**Wichtig:** Wir verbinden uns **nicht** mit dem normalen Tailscale-Login, sondern mit unserem
eigenen Lab-Server. Deshalb der `--login-server`-Parameter.

```bash
sudo tailscale up \
  --login-server https://<lab-headscale-PUBLIC-IP>:443 \
  --authkey <dein-pre-auth-key>
```

Die **Public-IP** des Lab-Headscale und dein **persönlicher Pre-Auth-Key** stehen in deiner
Onboarding-DM (der Key ist nur für dich, 72h gültig).

> ⚠️ **Wenn du Tailscale schon privat nutzt:** Der `--login-server` ist Pflicht, sonst landest du
> im falschen Netz. Nach dem Spieltag kommst du mit `sudo tailscale logout && sudo tailscale up`
> wieder in dein normales Tailnet zurück.

> 📷 *[Screenshot-Platzhalter: erfolgreicher `tailscale up`-Login]*

---

## Schritt 3 — Verbindung testen

```bash
sudo tailscale status
```

Du solltest die Lab-Hosts sehen. Dann verbinde dich mit **deiner** Workstation (genaue
Zugangsdaten — User/Host/Passwort — bekommst du in der Onboarding-DM bzw. im Warm-up):

- **Red-Team:** `ssh player<N>@10.99.30.<N+2>`  (z.B. `player1@10.99.30.3`)
- **Blue-Team:** `ssh <user>@10.99.20.<N+2>`  (z.B. `…@10.99.20.3`)

> Passwörter werden **nicht** hier verteilt, sondern out-of-band (DM/Warm-up).

> 📷 *[Screenshot-Platzhalter: `tailscale status` mit sichtbaren Lab-Hosts]*

Klappt der SSH-Login? **Glückwunsch, du bist drin.** Falls nicht: kein Stress, das klären wir
gemeinsam im Warm-up-Block 1.

---

## Schritt 4 — Telegram-Channel beitreten

Du bekommst einen Einladungslink zu deinem Team-Channel:

- **Red:** `cyber-range-red`
- **Blue:** `cyber-range-blue`

Dort sitzt **Hermes**, der KI-Spielleiter. Du kannst ihn **alles fragen** — er gibt gestufte Hints
(erst ein Schubs, dann konkreter), niemals direkt den ganzen Spoiler, und nie etwas vom anderen Team.

Beispiele:
- Red: *„Wie umgeh ich das WordPress-Login-Rate-Limit?"*
- Blue: *„Wie finde ich failed SSH-Logins in Wazuh?"*
- Beide: *„Was war nochmal die Pyramid of Pain?"*

---

## Dein Tag (Überblick)

| Block | Dauer | Was passiert |
|---|---|---|
| Warm-up | 90 min | Onboarding, Lab-Map, Tool-Walkthrough, Team-Briefing |
| Runde 1 | 2.5 h | Erste Phasen der Übung |
| Pause / Analyse | 30 min | Snapshot, kurze Standortbestimmung |
| Runde 2 | 2.5 h | Weitere Phasen |
| Debrief | 1 h | Gemeinsame Auswertung — was lief, was lernen wir? |

Im Warm-up bekommst du dein vollständiges **Team-Briefing** (Red oder Blue) mit allen Details.

---

## Spielregeln in einem Satz

> Greife **nur** die Lab-Zielsysteme an, **niemals** etwas außerhalb des Labs — und hab Spaß beim Lernen.

Bei Fragen vor dem Spieltag: melde dich bei André. Bis dann! 🚩🛡️
