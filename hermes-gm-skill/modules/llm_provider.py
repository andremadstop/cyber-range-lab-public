"""llm_provider.py — LLM-Provider-Adapter fuer Hermes-GM.

Unterstuetzt Gemini (Default) und DeepSeek als Fallback.
Nutzt einfache REST-API-Aufrufe statt SDK-Abhaengigkeiten.
"""

import json
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class LLMProvider:
    """Abstrakter LLM-Provider fuer Hint- und Report-Generierung."""

    def __init__(
        self,
        provider: str = "gemini",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv("GM_LLM_API_KEY", "")
        self.model = model or self._default_model()

    def _default_model(self) -> str:
        if self.provider == "gemini":
            return "gemini-2.5-flash"
        elif self.provider == "deepseek":
            return "deepseek-chat"
        return "gemini-2.5-flash"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generiert eine Antwort ueber den konfigurierten Provider.

        Args:
            system_prompt: System-Prompt mit Rollen-Instruktionen.
            user_prompt: User-Nachricht / Frage.
            temperature: Kreativitaet (0.0-1.0).
            max_tokens: Maximale Token-Anzahl der Antwort.

        Returns:
            Generierte Antwort als String.
        """
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt, temperature, max_tokens)
        elif self.provider == "deepseek":
            return self._call_deepseek(system_prompt, user_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unbekannter Provider: {self.provider}")

    def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Ruft die Google Gemini API auf."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
        except Exception as e:
            logger.error("Gemini API-Fehler: %s", e)
            return f"[LLM-Fehler: {e}]"

    def _call_deepseek(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Ruft die DeepSeek API auf."""
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error("DeepSeek API-Fehler: %s", e)
            return f"[LLM-Fehler: {e}]"
