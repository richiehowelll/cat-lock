import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault(
    "screeninfo",
    SimpleNamespace(get_monitors=lambda: []),
)

from src.ui.overlay_geometry import (
    compute_overlay_geometry,
    get_monitor_fingerprint,
    get_monitor_options,
    get_target_monitor,
)


class OverlayGeometryTest(unittest.TestCase):
    def test_uses_primary_monitor_when_available(self):
        secondary = SimpleNamespace(x=0, y=0, width=1280, height=720)
        primary = SimpleNamespace(x=1280, y=0, width=1920, height=1080, is_primary=True)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[secondary, primary]):
            self.assertIs(get_target_monitor(), primary)

    def test_uses_configured_monitor_when_available(self):
        first = SimpleNamespace(x=0, y=0, width=1280, height=720, is_primary=True)
        second = SimpleNamespace(x=1280, y=0, width=1920, height=1080)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[first, second]):
            self.assertIs(get_target_monitor(1), second)
            self.assertIs(get_target_monitor(99), first)

    def test_fingerprint_match_takes_precedence_over_monitor_index(self):
        primary = SimpleNamespace(x=0, y=0, width=1280, height=720, is_primary=True)
        selected = SimpleNamespace(x=1280, y=0, width=1920, height=1080)
        reordered_selected = SimpleNamespace(x=1280, y=0, width=1920, height=1080)
        reordered_primary = SimpleNamespace(x=0, y=0, width=1280, height=720, is_primary=True)
        fingerprint = {
            "x": 1280,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "isPrimary": False,
        }

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[primary, selected]):
            self.assertIs(get_target_monitor(1, fingerprint), selected)

        with patch(
            "src.ui.overlay_geometry.get_monitors",
            return_value=[reordered_selected, reordered_primary],
        ):
            self.assertIs(get_target_monitor(1, fingerprint), reordered_selected)

    def test_computes_centered_geometry_and_clamps_y_percent(self):
        monitor = SimpleNamespace(x=100, y=50, width=1000, height=800, is_primary=True)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[monitor]):
            self.assertEqual(
                compute_overlay_geometry(-10, overlay_width=400, overlay_height=100),
                (400, 100, 400, 50),
            )
            self.assertEqual(
                compute_overlay_geometry(150, overlay_width=400, overlay_height=100),
                (400, 100, 400, 750),
            )
            self.assertEqual(
                compute_overlay_geometry("bad", overlay_width=400, overlay_height=100),
                (400, 100, 400, 225),
            )

    def test_computes_geometry_on_selected_monitor(self):
        first = SimpleNamespace(x=0, y=0, width=1000, height=800, is_primary=True)
        second = SimpleNamespace(x=1000, y=100, width=800, height=600)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[first, second]):
            self.assertEqual(
                compute_overlay_geometry(
                    50,
                    overlay_width=400,
                    overlay_height=100,
                    monitor_index=1,
                ),
                (400, 100, 1200, 350),
            )

    def test_monitor_options_include_primary_marker(self):
        first = SimpleNamespace(x=0, y=0, width=1000, height=800, is_primary=True)
        second = SimpleNamespace(x=1000, y=0, width=800, height=600)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[first, second]):
            self.assertEqual(
                get_monitor_options(),
                [
                    (0, "Monitor 1: 1000x800 (primary)"),
                    (1, "Monitor 2: 800x600"),
                ],
            )

    def test_monitor_fingerprint_for_selected_monitor(self):
        monitor = SimpleNamespace(x=-800, y=100, width=800, height=600, is_primary=False)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[monitor]):
            self.assertEqual(
                get_monitor_fingerprint(0),
                {
                    "x": -800,
                    "y": 100,
                    "width": 800,
                    "height": 600,
                    "isPrimary": False,
                },
            )
            self.assertIsNone(get_monitor_fingerprint(9))


if __name__ == "__main__":
    unittest.main()
