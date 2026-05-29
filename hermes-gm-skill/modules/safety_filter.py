"""safety_filter.py — Verhindert Token-Leaks in Outbound-Messages.

Scant alle ausgehenden Nachrichten auf sensible Patterns (API-Keys,
JWTs, SSH-Keys) und redact-ed diese automatisch. Pflicht-Filter
fuer alle Telegram-Outbound-Nachrichten.
"""

import re
from typing import Optional


# Regex-Patterns fuer sensible Daten
SENSITIVE_PATTERNS = {
    "hetzner_api_token": re.compile(
        r"[a-zA-Z0-9]{64}", re.IGNORECASE
    ),
    "jwt_token": re.compile(
        r"eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+"
    ),
    "ssh_private_key": re.compile(
        r"-----BEGIN (RSA |EC |ED25519 |OPENSSH )?PRIVATE KEY-----"
    ),
    "telegram_bot_token": re.compile(
        r"\d{8,10}:[a-zA-Z0-9_-]{35}"
    ),
    "github_token": re.compile(
        r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}"
    ),
    "generic_api_key": re.compile(
        r"(?:api[_-]?key|apikey|token|secret)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}['\"]?",
        re.IGNORECASE,
    ),
}

# Ausnahmen: bekannte harmlose Strings mit 64 Zeichen
ALLOWLIST = {
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
}


def scan_message(message: str) -> tuple[str, list[str]]:
    """Scannt eine Nachricht auf sensible Patterns.

    Args:
        message: Die zu scannende Nachricht.

    Returns:
        Tuple aus (gesaeuberte Nachricht, Liste der gefundenen Pattern-Typen).
    """
    found_patterns: list[str] = []
    cleaned = message

    for pattern_name, pattern in SENSITIVE_PATTERNS.items():
        matches = pattern.findall(cleaned)
        for match in matches:
            if match in ALLOWLIST:
                continue
            cleaned = cleaned.replace(match, f"[REDACTED:{pattern_name}]")
            if pattern_name not in found_patterns:
                found_patterns.append(pattern_name)

    return cleaned, found_patterns


def validate_outbound(message: str) -> str:
    """Validiert eine ausgehende Nachricht und redact-ed sie.

    Diese Funktion MUSS vor jeder Telegram-Outbound-Nachricht aufgerufen werden.

    Args:
        message: Die zu validierende Nachricht.

    Returns:
        Die gesaeuberte Nachricht (ggf. mit Redactions).
    """
    cleaned, patterns = scan_message(message)
    if patterns:
        import logging
        logging.warning(
            "safety_filter: %s in outbound message redacted",
            ", ".join(patterns),
        )
    return cleaned


def is_safe(message: str) -> bool:
    """Prueft ob eine Nachricht sicher ist (keine Sensitive-Daten enthaelt).

    Args:
        message: Die zu pruefende Nachricht.

    Returns:
        True wenn keine sensiblen Daten gefunden wurden.
    """
    _, patterns = scan_message(message)
    return len(patterns) == 0
