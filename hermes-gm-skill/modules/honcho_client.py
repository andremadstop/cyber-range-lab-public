"""honcho_client.py — Spielerprofile lesen/schreiben.

Honcho ist das Theory-of-Mind-System. Es speichert Spielerprofile
(Skill-Levels, Lernfortschritt, Hint-Statistiken) und erlaubt
Hermes-GM adaptives Hinting basierend auf Spieler-Faehigkeiten.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# Default-Profil fuer neue Spieler (Honcho-Ausfall-Fallback)
DEFAULT_PLAYER_PROFILE = {
    "skill_level_inferred": {
        "siem": 2,
        "forensics": 1,
        "network": 2,
        "web": 2,
    },
    "hints_received_today": 0,
    "hints_helpful_ratio": 0.8,
    "struggling_with": [],
    "favorite_tools": [],
}


class HonchoClient:
    """Client fuer Honcho-Spielerprofile via REST/gRPC."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        app_name: str = "cyber-range-coach",
        session_id: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("HONCHO_API_KEY", "")
        self.app_name = app_name
        self.session_id = session_id or f"pilot-{datetime.now().strftime('%Y-%m-%d')}"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_player_profile(self, player_id: str) -> dict[str, Any]:
        """Liest das Profil eines Spielers.

        Args:
            player_id: Eindeutige Spieler-ID (pseudonymisiert).

        Returns:
            Spielerprofil als Dict, ggf. Default bei Fehler.
        """
        url = f"{self.base_url}/api/v1/apps/{self.app_name}/sessions/{self.session_id}/users/{player_id}"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("profile", DEFAULT_PLAYER_PROFILE.copy())
        except Exception as e:
            logger.warning(
                "Honcho-Read-Fehler fuer %s: %s -> Fallback auf Default",
                player_id, e,
            )
            return DEFAULT_PLAYER_PROFILE.copy()

    def update_player_profile(
        self,
        player_id: str,
        profile_updates: dict[str, Any],
    ) -> bool:
        """Aktualisiert das Profil eines Spielers.

        Args:
            player_id: Spieler-ID.
            profile_updates: Zu aktualisierende Felder.

        Returns:
            True bei Erfolg.
        """
        url = f"{self.base_url}/api/v1/apps/{self.app_name}/sessions/{self.session_id}/users/{player_id}"
        try:
            current = self.get_player_profile(player_id)
            current.update(profile_updates)
            resp = requests.put(
                url, headers=self._headers(),
                json={"profile": current}, timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error("Honcho-Write-Fehler: %s", e)
            return False

    def record_hint(
        self,
        player_id: str,
        hint_text: str,
        helpful: Optional[bool] = None,
    ) -> bool:
        """Dokumentiert einen gegebenen Hint.

        Args:
            player_id: Spieler-ID.
            hint_text: Der gegebene Hint.
            helpful: Ob der Hint als hilfreich bewertet wurde.

        Returns:
            True bei Erfolg.
        """
        current = self.get_player_profile(player_id)
        hints = current.get("hints_received_today", 0)
        ratio = current.get("hints_helpful_ratio", 0.8)

        update = {"hints_received_today": hints + 1}
        if helpful is not None:
            new_ratio = ((ratio * hints) + (1.0 if helpful else 0.0)) / (hints + 1)
            update["hints_helpful_ratio"] = round(new_ratio, 2)

        return self.update_player_profile(player_id, update)

    def log_struggle(self, player_id: str, topic: str) -> bool:
        """Dokumentiert ein Thema mit dem ein Spieler strugglet.

        Args:
            player_id: Spieler-ID.
            topic: Thema (z.B. 'memory-forensics', 'dns-tunneling').

        Returns:
            True bei Erfolg.
        """
        current = self.get_player_profile(player_id)
        struggles = current.get("struggling_with", [])
        if topic not in struggles:
            struggles.append(topic)
        return self.update_player_profile(player_id, {"struggling_with": struggles})

    def health_check(self) -> bool:
        """Prueft ob Honcho erreichbar ist.

        Returns:
            True wenn API antwortet.
        """
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
