# Übungsvereinbarung — Cyber-Range Pilot

> **Einwilligungs- und Teilnahme-Template (DSGVO-konform)**
> **Veranstaltung:** Cyber-Range Red-Team-vs-Blue-Team-Training
> **Datum / Zeit:** ____________ (Mo 2026-06-01 / Di 2026-06-02), ca. 9:00–18:00 Uhr
> **Veranstalter:** [Veranstalter] · Andre
>
> Bitte vor Spielbeginn lesen und unterschreiben. Jede:r Teilnehmer:in bekommt ein Exemplar.

---

## 1. Worum es geht

Du nimmst freiwillig an einem Cybersecurity-Trainingsszenario teil. In einem isolierten Lab
(Hetzner-Cloud) greift ein Red-Team simulierte Zielsysteme an, während ein Blue-Team die Angriffe
mit einem SIEM (Wazuh) erkennt und analysiert. Ziel ist das Üben von Angriffs- und
Detection-Techniken im Rahmen unserer CySA+-Weiterbildung.

## 2. Lab-Isolation — keine externen Ziele

- Alle Aktivitäten finden **ausschließlich** innerhalb des abgeschotteten Lab-Netzwerks statt.
- Es werden **keine** realen, fremden oder produktiven Systeme angegriffen, gescannt oder getestet.
- Angriffstechniken, die du hier lernst, dürfen **außerhalb dieses Labs nur mit ausdrücklicher
  Erlaubnis des jeweiligen Systembetreibers** angewendet werden. Unbefugtes Eindringen in fremde
  Systeme ist strafbar (§ 202a ff. StGB).

## 3. Datenverarbeitung

- Während der Übung fallen **technische Logs** an (Wazuh-Alerts, Netzwerk-Telemetrie,
  Telegram-Channel-Verlauf, KI-Spielleiter-Interaktionen).
- Spielerprofile, die der KI-Spielleiter (Hermes) führt, sind **pseudonymisiert** — es werden keine
  Klarnamen, sondern nur Alias-IDs gespeichert.
- Logs und Profildaten werden **nach Abschluss des Pilots gelöscht oder anonymisiert archiviert**.
  Eine Archivierung in identifizierbarer Form erfolgt **nur mit deiner gesonderten Einwilligung**
  (Abschnitt 7).
- Du kannst die zu dir gehörenden pseudonymen Profildaten jederzeit löschen lassen
  (KI-Befehl `/forget-me` oder formlose Mitteilung an den Veranstalter).

## 4. Freiwilligkeit & Abbruch

- Die Teilnahme ist **freiwillig** und kostenlos.
- Teilnehmer:innen sind **volljährig** (oder mit Einverständnis der Erziehungsberechtigten).
- Du kannst die Übung **jederzeit und ohne Angabe von Gründen abbrechen** — ohne Nachteil.

## 5. Schweigepflicht

- Inhalte der Übung — insbesondere Verhalten, Fragen oder Fehler einzelner Teilnehmer:innen —
  werden **vertraulich** behandelt und nicht außerhalb der Gruppe geteilt.
- Erkenntnisse über Techniken und Tools dürfen für Lernzwecke frei verwendet werden;
  personenbezogene Beobachtungen nicht.

## 6. Haftungsausschluss

- Du nutzt für den Zugriff (SSH-/Tailscale-Client) **eigene Hardware**. Der Veranstalter
  **haftet nicht** für etwaige Beeinträchtigungen deiner eigenen Geräte, Software oder Daten.
- Die Lab-Zielsysteme sind absichtlich verwundbar — der Umgang damit erfolgt auf eigene
  Verantwortung im Rahmen der Übungsregeln.
- Es besteht **kein Anspruch** auf ununterbrochene Verfügbarkeit des Labs.

## 7. Foto / Video / Archivierung (optional)

Bitte ankreuzen:

- [ ] Ich willige ein, dass **Foto-/Video-Aufnahmen** während der Übung gemacht und für interne
      Kurs-Dokumentation verwendet werden dürfen.
- [ ] Ich willige ein, dass meine **pseudonymen Übungsdaten** für einen anonymisierten
      Lessons-Learned-Report ausgewertet und archiviert werden dürfen.

(Ohne Ankreuzen: keine Aufnahmen von dir, keine identifizierbare Archivierung.)

---

## Einwilligung

Ich habe die Übungsvereinbarung gelesen und bin mit den Bedingungen einverstanden.

| | |
|---|---|
| Name (Klarname, bleibt beim Veranstalter) | ____________________________ |
| Gewählter Alias (für Lab/Profil) | ____________________________ |
| Team (Red / Blue) | ____________________________ |
| Ort, Datum | ____________________________ |
| Unterschrift | ____________________________ |

---

> **Hinweis Veranstalter:** Klarnamen werden ausschließlich auf diesem Papier-/PDF-Dokument
> gehalten, **nie** in committeten Dateien, Logs oder KI-Profilen. Das Mapping Alias→Klarname
> verbleibt offline beim Veranstalter und wird nach dem Pilot vernichtet.
