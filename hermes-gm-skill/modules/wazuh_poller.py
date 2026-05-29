"""wazuh_poller.py — Pollt die Wazuh-API alle 2 Minuten.

Erkennt neue Alerts, klassifiziert sie nach MITRE-Technique und
erkennt Stillstand (keine neuen Alerts >30 min).
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class WazuhPoller:
    """Pollt die Wazuh-API und liefert Alert-Informationen."""

    def __init__(
        self,
        base_url: str = "https://10.99.20.2",
        username: Optional[str] = None,
        password: Optional[str] = None,
        poll_interval_seconds: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username or os.getenv("WAZUH_API_USER", "admin")
        self.password = password or os.getenv("WAZUH_API_PASSWORD", "CHANGEME_set_in_your_vault")
        self.poll_interval = poll_interval_seconds
        self._jwt_token: Optional[str] = None
        self._last_alert_timestamp: Optional[str] = None
        self._last_poll_time: Optional[float] = None
        self._consecutive_empty_polls = 0

    def _get_jwt(self) -> str:
        """Authentifiziert sich bei der Wazuh-API und holt JWT."""
        url = f"{self.base_url}:55000/security/user/authenticate"
        try:
            resp = requests.post(
                url,
                auth=(self.username, self.password),
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            self._jwt_token = data.get("data", {}).get("token", "")
            return self._jwt_token or ""
        except Exception as e:
            logger.error("Wazuh-Auth-Fehler: %s", e)
            return ""

    def _headers(self) -> dict[str, str]:
        if not self._jwt_token:
            self._get_jwt()
        return {
            "Authorization": f"Bearer {self._jwt_token}",
            "Content-Type": "application/json",
        }

    def get_alerts(
        self,
        limit: int = 50,
        min_level: int = 8,
    ) -> list[dict[str, Any]]:
        """Holt die aktuellen Alerts ab Level >= min_level.

        Args:
            limit: Maximale Anzahl Alerts.
            min_level: Mindest-Alert-Level (Wazuh-Level 0-15).

        Returns:
            Liste der Alerts (dicts).
        """
        url = f"{self.base_url}:55000/security/alerts"
        params = {
            "limit": limit,
            "sort": "-timestamp",
            "filters": {"rule.level": f">{min_level - 1}"},
        }
        try:
            resp = requests.get(
                url,
                headers=self._headers(),
                params=params,
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            alerts = data.get("data", {}).get("affected_items", [])

            if not alerts:
                self._consecutive_empty_polls += 1
            else:
                self._consecutive_empty_polls = 0
                self._last_alert_timestamp = alerts[0].get("timestamp")

            self._last_poll_time = time.time()
            return alerts
        except Exception as e:
            logger.error("Wazuh-API-Fehler: %s", e)
            return []

    def get_new_alerts_since_last_poll(self) -> list[dict[str, Any]]:
        """Holt nur Alerts seit dem letzten Poll.

        Returns:
            Liste neuer Alerts.
        """
        all_alerts = self.get_alerts(limit=100)
        if not self._last_alert_timestamp:
            # Erster Poll: gib die aktuellen zurueck
            return all_alerts[:10] if all_alerts else []

        new_alerts = []
        for alert in all_alerts:
            if alert.get("timestamp") == self._last_alert_timestamp:
                break
            new_alerts.append(alert)

        if new_alerts:
            self._last_alert_timestamp = new_alerts[0].get("timestamp")
            self._consecutive_empty_polls = 0

        return new_alerts

    def is_still(self, threshold_minutes: int = 30) -> bool:
        """Prueft ob Stillstand herrscht (keine neuen Alerts seit X min).

        Args:
            threshold_minutes: Minuten ohne neue Alerts fuer Stillstand.

        Returns:
            True wenn Stillstand.
        """
        if self._last_poll_time is None:
            return False
        elapsed = (time.time() - self._last_poll_time) / 60
        return elapsed > threshold_minutes

    def get_alert_stats(self) -> dict[str, int]:
        """Holt Statistik zu Alert-Leveln.

        Returns:
            Dict mit Level -> Count.
        """
        alerts = self.get_alerts(limit=200, min_level=3)
        stats: dict[str, int] = {}
        for alert in alerts:
            level = str(alert.get("rule", {}).get("level", 0))
            stats[level] = stats.get(level, 0) + 1
        return stats

    def health_check(self) -> bool:
        """Prueft ob die Wazuh-API erreichbar ist.

        Returns:
            True wenn API antwortet.
        """
        try:
            resp = requests.get(
                f"{self.base_url}:55000",
                verify=False,
                timeout=10,
            )
            return resp.status_code in [200, 401]
        except Exception:
            return False
