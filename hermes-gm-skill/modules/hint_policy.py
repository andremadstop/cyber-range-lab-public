"""hint_policy.py — Stillstand-Erkennung + adaptive Hint-Tiefe.

Entscheidet WANN (Stillstand >30min) und WIE (subtle/medium/direct)
ein Hint gegeben wird. Nutzt Spielerprofile aus Honcho zur
Kalibrierung der Hint-Tiefe.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HintPolicy:
    """Politik fuer Hint-Generierung und Stillstand-Erkennung."""

    def __init__(
        self,
        cooldown_minutes: int = 5,
        max_hints_per_hour: int = 6,
        stillness_threshold_minutes: int = 30,
    ):
        self.cooldown_seconds = cooldown_minutes * 60
        self.max_hints_per_hour = max_hints_per_hour
        self.stillness_threshold = stillness_threshold_minutes
        self._hint_log: list[dict[str, Any]] = []
        self._last_activity_per_team: dict[str, float] = {}

    def record_activity(self, team: str):
        """Dokumentiert Aktivitaet eines Teams.

        Args:
            team: 'red', 'blue' oder 'gm'.
        """
        self._last_activity_per_team[team] = time.time()

    def get_inactivity_minutes(self, team: str) -> float:
        """Berechnet Inaktivitaet eines Teams in Minuten.

        Args:
            team: 'red', 'blue' oder 'gm'.

        Returns:
            Minuten seit letzter Aktivitaet (0.0 wenn keine Aktivitaet bekannt).
        """
        last = self._last_activity_per_team.get(team, 0.0)
        if last == 0.0:
            return 0.0
        return (time.time() - last) / 60

    def is_still(self, team: str) -> bool:
        """Prueft ob ein Team im Stillstand ist.

        Args:
            team: 'red', 'blue' oder 'gm'.

        Returns:
            True wenn Team > threshold Minuten inaktiv.
        """
        inactive = self.get_inactivity_minutes(team)
        return inactive > self.stillness_threshold

    def can_send_hint(self, player_id: str) -> bool:
        """Prueft ob einem Spieler ein Hint geschickt werden darf.

        Beruecksichtigt Cooldown und Max-Hints-Pro-Stunde.

        Args:
            player_id: Spieler-ID.

        Returns:
            True wenn Hint gesendet werden darf.
        """
        now = time.time()
        one_hour_ago = now - 3600

        # Hints des Spielers in der letzten Stunde
        recent_hints = [
            h for h in self._hint_log
            if h["player_id"] == player_id and h["timestamp"] > one_hour_ago
        ]

        if len(recent_hints) >= self.max_hints_per_hour:
            logger.info("Hint-Limit fuer %s erreicht (%d/h)", player_id, self.max_hints_per_hour)
            return False

        # Cooldown: letzter Hint muss > cooldown_seconds zurueck liegen
        if recent_hints:
            last_hint_time = max(h["timestamp"] for h in recent_hints)
            if (now - last_hint_time) < self.cooldown_seconds:
                logger.info("Cooldown aktiv fuer %s", player_id)
                return False

        return True

    def determine_hint_depth(
        self,
        player_skill: int,
        stillness_minutes: float,
    ) -> str:
        """Ermittelt die angemessene Hint-Tiefe.

        Args:
            player_skill: Skill-Level (1-5).
            stillness_minutes: Minuten seit letzter Aktion.

        Returns:
            'subtle', 'medium' oder 'direct'.
        """
        # Bei langem Stillstand direkter helfen
        if stillness_minutes > 60:
            return "direct"
        elif stillness_minutes > 45:
            return "medium"

        # Skill-basierte Tiefe
        if player_skill <= 2:
            return "medium"
        elif player_skill <= 4:
            return "subtle"
        else:
            return "subtle"

    def log_hint(
        self,
        player_id: str,
        team: str,
        hint_text: str,
        hint_depth: str,
    ):
        """Dokumentiert einen gegebenen Hint fuer Cooldown-Tracking.

        Args:
            player_id: Spieler-ID.
            team: 'red', 'blue' oder 'gm'.
            hint_text: Der gegebene Hint.
            hint_depth: 'subtle', 'medium' oder 'direct'.
        """
        self._hint_log.append({
            "player_id": player_id,
            "team": team,
            "hint_text": hint_text[:100],
            "hint_depth": hint_depth,
            "timestamp": time.time(),
        })

    def get_team_hint_count(self, team: str, minutes_back: int = 30) -> int:
        """Zaehlt Hints fuer ein Team in den letzten X Minuten.

        Args:
            team: 'red', 'blue' oder 'gm'.
            minutes_back: Zeitfenster in Minuten.

        Returns:
            Anzahl Hints.
        """
        cutoff = time.time() - (minutes_back * 60)
        return sum(
            1 for h in self._hint_log
            if h["team"] == team and h["timestamp"] > cutoff
        )
