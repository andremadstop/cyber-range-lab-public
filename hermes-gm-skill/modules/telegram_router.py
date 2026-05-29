"""telegram_router.py — 3-Channel-Routing fuer Hermes-GM.

Leitet Nachrichten basierend auf dem Channel (red/blue/gm) an die
richtige Stelle und stellt team-spezifischen Kontext bereit.
Nutzt python-telegram-bot fuer die Bot-Integration.
"""

import logging
from typing import Any, Optional

from safety_filter import validate_outbound

logger = logging.getLogger(__name__)

# Channel-Konstanten
CHANNEL_RED = "cyber-range-red"
CHANNEL_BLUE = "cyber-range-blue"
CHANNEL_GM = "cyber-range-gm"


class TelegramRouter:
    """Router fuer 3 Telegram-Channels mit team-spezifischem Kontext."""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token
        self._bot = None
        # Channel-ID Mapping (wird beim Start konfiguriert)
        self.channels: dict[str, str] = {
            CHANNEL_RED: "",
            CHANNEL_BLUE: "",
            CHANNEL_GM: "",
        }

    def configure_channel(self, name: str, chat_id: str):
        """Konfiguriert einen Channel.

        Args:
            name: Channel-Name (cyber-range-red/blue/gm).
            chat_id: Telegram-Chat-ID.
        """
        if name in self.channels:
            self.channels[name] = chat_id

    def get_team_for_channel(self, channel_name: str) -> str:
        """Ermittelt das Team fuer einen Channel.

        Args:
            channel_name: Name des Channels.

        Returns:
            'red', 'blue', 'gm' oder 'unknown'.
        """
        if "red" in channel_name:
            return "red"
        elif "blue" in channel_name:
            return "blue"
        elif "gm" in channel_name:
            return "gm"
        return "unknown"

    def send_message(self, channel: str, message: str) -> bool:
        """Sendet eine Nachricht an einen Channel (mit Safety-Filter).

        Args:
            channel: Channel-Name.
            message: Nachrichtentext.

        Returns:
            True bei Erfolg.
        """
        safe_message = validate_outbound(message)
        chat_id = self.channels.get(channel, "")
        if not chat_id:
            logger.warning("Channel %s nicht konfiguriert", channel)
            return False

        # Placeholder: hier wuerde der echte Telegram-API-Call stehen
        logger.info(
            "[TELEGRAM -> %s] %s...", channel, safe_message[:100]
        )
        return True

    def send_to_team(self, team: str, message: str) -> bool:
        """Sendet Nachricht ans Team (red/blue), CC an GM.

        Args:
            team: 'red', 'blue' oder 'gm'.
            message: Nachricht.

        Returns:
            True bei Erfolg.
        """
        channel_map = {"red": CHANNEL_RED, "blue": CHANNEL_BLUE, "gm": CHANNEL_GM}
        channel = channel_map.get(team, CHANNEL_GM)
        success = self.send_message(channel, message)

        # CC an GM (aber nicht wenn GM selbst)
        if team != "gm":
            gm_message = f"[CC from {team}] {message[:200]}"
            self.send_message(CHANNEL_GM, gm_message)

        return success
