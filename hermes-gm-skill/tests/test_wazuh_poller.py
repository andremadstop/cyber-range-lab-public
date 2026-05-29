"""Tests fuer wazuh_poller — Wazuh-API-Polling."""

import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.wazuh_poller import WazuhPoller


class TestWazuhPoller:
    """Testet Wazuh-API-Poller."""

    def test_init(self):
        """Poller wird mit Defaults korrekt initialisiert."""
        poller = WazuhPoller(base_url="https://10.99.20.2")
        assert poller.base_url == "https://10.99.20.2"
        assert poller.poll_interval == 120

    @patch("modules.wazuh_poller.requests.get")
    def test_health_check_offline(self, mock_get):
        """Health-Check schlaegt fehl bei ConnectionError."""
        mock_get.side_effect = ConnectionError("offline")
        poller = WazuhPoller(base_url="https://10.99.99.99")
        assert not poller.health_check()

    @patch("modules.wazuh_poller.requests.post")
    @patch("modules.wazuh_poller.requests.get")
    def test_get_alerts_empty_when_offline(self, mock_get, mock_post):
        """get_alerts gibt leere Liste bei API-Fehler."""
        mock_post.side_effect = ConnectionError("offline")
        mock_get.side_effect = ConnectionError("offline")
        poller = WazuhPoller(base_url="https://10.99.99.99")
        alerts = poller.get_alerts()
        assert alerts == []

    def test_is_still_initially_false(self):
        """Direkt nach Initialisierung kein Stillstand."""
        poller = WazuhPoller()
        assert not poller.is_still()

    @patch("modules.wazuh_poller.requests.post")
    @patch("modules.wazuh_poller.requests.get")
    def test_alert_stats_empty_when_offline(self, mock_get, mock_post):
        """Alert-Stats geben leeres Dict bei API-Fehler."""
        mock_post.side_effect = ConnectionError("offline")
        mock_get.side_effect = ConnectionError("offline")
        poller = WazuhPoller(base_url="https://10.99.99.99")
        stats = poller.get_alert_stats()
        assert stats == {}
