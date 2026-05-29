"""Tests fuer hint_policy — Stillstand-Erkennung + Hint-Tiefe."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.hint_policy import HintPolicy


class TestHintPolicy:
    """Testet Hint-Politik und Stillstand-Erkennung."""

    def setup_method(self):
        self.policy = HintPolicy(
            cooldown_minutes=0,  # Kein Cooldown fuer Tests
            max_hints_per_hour=10,
            stillness_threshold_minutes=0.01,  # Sehr kurz fuer Tests
        )

    def test_initial_no_stillness(self):
        """Direkt nach Initialisierung kein Stillstand."""
        assert not self.policy.is_still("red")

    def test_stillness_detected(self):
        """Nach Inaktivitaet wird Stillstand erkannt."""
        policy = HintPolicy(stillness_threshold_minutes=10)
        import time as _time
        # Activity 20 min in der Vergangenheit simulieren
        policy._last_activity_per_team["red"] = _time.time() - (20 * 60)
        assert policy.is_still("red")

    def test_activity_resets_stillness(self):
        """Aktivitaet setzt Stillstand zurueck."""
        policy = HintPolicy(stillness_threshold_minutes=30)
        policy.record_activity("red")
        assert not policy.is_still("red")

    def test_can_send_hint(self):
        """Hint darf gesendet werden (innerhalb Limits)."""
        assert self.policy.can_send_hint("player-1")

    def test_hint_limit_exceeded(self):
        """Nach max Hints wird gesperrt."""
        for _ in range(10):
            self.policy.log_hint("player-1", "red", "test", "subtle")
        assert not self.policy.can_send_hint("player-1")

    def test_determine_hint_depth_beginner(self):
        """Anfaenger bekommen medium/direct Hints."""
        depth = self.policy.determine_hint_depth(player_skill=1, stillness_minutes=30)
        assert depth in ["medium", "direct"]

    def test_determine_hint_depth_expert(self):
        """Experten bekommen subtile Hints."""
        depth = self.policy.determine_hint_depth(player_skill=5, stillness_minutes=10)
        assert depth == "subtle"

    def test_determine_hint_depth_long_stillness(self):
        """Bei langem Stillstand wird direkter."""
        depth = self.policy.determine_hint_depth(player_skill=5, stillness_minutes=61)
        assert depth == "direct"

    def test_team_hint_count(self):
        """Team-Hint-Zaehlung funktioniert."""
        self.policy.log_hint("p1", "red", "hint1", "subtle")
        self.policy.log_hint("p2", "red", "hint2", "medium")
        self.policy.log_hint("p3", "blue", "hint3", "direct")

        assert self.policy.get_team_hint_count("red", minutes_back=60) == 2
        assert self.policy.get_team_hint_count("blue", minutes_back=60) == 1
