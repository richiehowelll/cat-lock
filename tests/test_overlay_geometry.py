import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault(
    "screeninfo",
    SimpleNamespace(get_monitors=lambda: []),
)

from src.ui.overlay_geometry import compute_overlay_geometry, get_target_monitor


class OverlayGeometryTest(unittest.TestCase):
    def test_uses_primary_monitor_when_available(self):
        secondary = SimpleNamespace(x=0, y=0, width=1280, height=720)
        primary = SimpleNamespace(x=1280, y=0, width=1920, height=1080, is_primary=True)

        with patch("src.ui.overlay_geometry.get_monitors", return_value=[secondary, primary]):
            self.assertIs(get_target_monitor(), primary)

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


if __name__ == "__main__":
    unittest.main()
