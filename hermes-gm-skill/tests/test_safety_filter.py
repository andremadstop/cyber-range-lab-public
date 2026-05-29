"""Tests fuer safety_filter — Token-Leak-Praevention."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.safety_filter import scan_message, validate_outbound, is_safe


class TestSafetyFilter:
    """Testet Token-Leak-Praevention."""

    def test_hetzner_token(self):
        """64-Zeichen-Hetzner-Token wird erkannt."""
        msg = "Mein Token ist a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:hetzner_api_token]" in cleaned
        assert "hetzner_api_token" in patterns

    def test_jwt_token(self):
        """JWT-Token wird erkannt."""
        msg = "JWT: eyJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoiMSJ9.abc123"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:jwt_token]" in cleaned

    def test_ssh_key(self):
        """SSH-Privater-Key wird erkannt."""
        msg = "-----BEGIN OPENSSH PRIVATE KEY-----\nabc123\n-----END OPENSSH PRIVATE KEY-----"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:ssh_private_key]" in cleaned

    def test_telegram_token(self):
        """Telegram-Bot-Token wird erkannt."""
        msg = "Bot-Token: 1234567890:ABCdefGHIjklmNOPqrstUVwxyzabcdefghijkl"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:telegram_bot_token]" in cleaned

    def test_github_token(self):
        """GitHub-Token wird erkannt."""
        msg = "ghp_abcdefghijklmnopqrstuvwxyz1234567890abcd"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:github_token]" in cleaned

    def test_generic_api_key(self):
        """Generischer API-Key wird erkannt."""
        msg = "api_key = super-secret-key-12345"
        cleaned, patterns = scan_message(msg)
        assert "[REDACTED:generic_api_key]" in cleaned

    def test_harmless_message(self):
        """Normale Nachricht bleibt unveraendert."""
        msg = "Hallo Team, startet mit nmap auf 10.99.10.0/28"
        cleaned, patterns = scan_message(msg)
        assert cleaned == msg
        assert patterns == []

    def test_validate_outbound(self):
        """validate_outbound redact-ed sicher."""
        msg = "Token=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        cleaned = validate_outbound(msg)
        assert cleaned != msg
        assert "aaaaaaaaaaaaaaaa" not in cleaned

    def test_is_safe_positive(self):
        """is_safe erkennt unsichere Nachrichten."""
        assert not is_safe("Token: eyJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoifQ.abc123")
        assert is_safe("Alles sicher hier")


class TestSafetyFilterEdgeCases:
    """Edge Cases fuer safety_filter."""

    def test_empty_message(self):
        """Leere Nachricht sollte keine Fehler werfen."""
        cleaned, patterns = scan_message("")
        assert cleaned == ""
        assert patterns == []

    def test_partial_token(self):
        """Unvollstaendige Tokens werden nicht als false-positive erkannt."""
        cleaned, _ = scan_message("eyJh")
        assert "REDACTED" not in cleaned

    def test_allowlist(self):
        """Allowlist-Eintraege werden ignoriert."""
        msg = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        cleaned, patterns = scan_message(msg)
        assert "REDACTED" not in cleaned
        assert patterns == []
