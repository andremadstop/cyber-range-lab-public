"""report_generator.py — Lessons-Learned-Report nach Spielende.

Generiert einen strukturierten Report aus Wazuh-Alert-Daten,
Telegram-History und Honcho-Insights. Nutzt LLM fuer die
Text-Generierung.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml
from jinja2 import Template

from llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generiert Lessons-Learned-Reports."""

    def __init__(
        self,
        output_dir: str = "lessons-learned",
        llm_provider: Optional[LLMProvider] = None,
        context_path: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm = llm_provider or LLMProvider(provider="gemini", model="gemini-2.5-pro")
        self.context = self._load_context(context_path)

    def _load_context(self, path: Optional[str] = None) -> dict[str, Any]:
        """Laedt den statischen Spielkontext aus gm_context.yaml."""
        path = path or os.path.join(
            os.path.dirname(__file__), "..", "gm_context.yaml"
        )
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning("Konnte gm_context.yaml nicht laden: %s", e)
            return {}

    def generate(
        self,
        wazuh_alerts: list[dict[str, Any]],
        player_stats: list[dict[str, Any]],
        game_start: str,
        game_end: Optional[str] = None,
    ) -> str:
        """Generiert einen vollstaendigen Lessons-Learned-Report.

        Args:
            wazuh_alerts: Alle Wazuh-Alerts des Spielzeitraums.
            player_stats: Spieler-Statistiken aus Honcho.
            game_start: ISO-Startzeit.
            game_end: ISO-Endzeit (Default: jetzt).

        Returns:
            Report als Markdown-String.
        """
        game_end = game_end or datetime.now(timezone.utc).isoformat()

        # Alert-Statistiken berechnen
        alert_stats = self._compute_alert_stats(wazuh_alerts)
        critical_misses = self._find_critical_misses(wazuh_alerts)
        phase_progress = self._compute_phase_progress(wazuh_alerts)

        # Template laden
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "report.j2"
        )
        try:
            with open(template_path) as f:
                template = Template(f.read())
        except Exception:
            # Fallback-Template
            template = Template("""# Lessons Learned — {{ game_date }}

## Executive Summary
- Spielzeit: {{ duration_hours }} Stunden
- Red-Team: {{ red_team_size }} Spieler
- Blue-Team: {{ blue_team_size }} Spieler
- Gesamt-Alerts: {{ total_alerts }}
""")

        # Prompt rendern
        prompt = template.render(
            game_date=game_start[:10],
            duration_hours=8,
            red_team_size=self.context.get("game", {}).get("red_team_size", 4),
            blue_team_size=self.context.get("game", {}).get("blue_team_size", 3),
            total_alerts=len(wazuh_alerts),
            alert_stats=alert_stats,
            critical_misses=critical_misses,
            phase_progress=phase_progress,
            player_stats=player_stats,
        )

        # LLM-Call
        report_text = self.llm.generate(
            system_prompt="Du bist ein erfahrener CySA+-Instructor. "
                          "Generiere einen praezisen Lessons-Learned-Report.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        # Report speichern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{game_start[:10]}_{timestamp}.md"
        try:
            with open(output_path, "w") as f:
                f.write(report_text)
            logger.info("Report gespeichert: %s", output_path)
        except Exception as e:
            logger.error("Konnte Report nicht speichern: %s", e)

        return report_text

    def _compute_alert_stats(
        self, alerts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Berechnet Alert-Statistiken per Rule."""
        from collections import Counter
        rule_counts: Counter = Counter()
        for alert in alerts:
            rule_id = str(alert.get("rule", {}).get("id", "unknown"))
            rule_counts[rule_id] += 1

        stats = []
        for rule_id, count in rule_counts.most_common():
            stats.append({
                "rule_id": rule_id,
                "name": f"Rule {rule_id}",
                "count": count,
                "investigated": 0,  # Platzhalter — echte Daten aus Telegram-History
            })
        return stats

    def _find_critical_misses(
        self, alerts: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        """Identifiziert kritische verpasste Alerts."""
        high_level_alerts = [
            a for a in alerts
            if a.get("rule", {}).get("level", 0) >= 10
        ]

        misses = []
        for alert in high_level_alerts[:5]:  # Top 5
            misses.append({
                "phase": alert.get("rule", {}).get("description", "Unknown"),
                "description": (
                    f"Rule {alert.get('rule', {}).get('id', '?')} auf Level "
                    f"{alert.get('rule', {}).get('level', 0)} nicht untersucht"
                ),
            })
        return misses

    def _compute_phase_progress(
        self, alerts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Berechnet Phasen-Fortschritt aus Alert-Daten."""
        phases = self.context.get("attack_phases", [])
        progress = []
        for phase in phases:
            progress.append({
                "id": phase.get("id", "?"),
                "name": phase.get("name", "?"),
                "red_reached": "ja",
                "blue_detected": "unbekannt",
            })
        return progress
