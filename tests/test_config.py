import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.config import config as config_module


class ConfigTest(unittest.TestCase):
    def test_load_copies_bundled_config_when_user_config_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            user_config_path = os.path.join(temp_dir, "config.json")
            bundled_config_path = os.path.join(temp_dir, "bundled.json")
            with open(bundled_config_path, "w", encoding="utf-8") as f:
                json.dump({"hotkey": "ctrl+shift+l"}, f)

            with patch("src.config.config.get_config_path", return_value=user_config_path), patch(
                "src.config.config.get_packaged_path",
                return_value=bundled_config_path,
            ):
                self.assertEqual(config_module.load(), {"hotkey": "ctrl+shift+l"})

            self.assertTrue(os.path.exists(user_config_path))

    def test_config_clamps_values_and_saves_migration_atomically(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            user_config_path = os.path.join(temp_dir, "config.json")
            with open(user_config_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "hotkey": "ctrl+x",
                        "opacity": 0.25,
                        "notificationsEnabled": False,
                        "overlayYPercent": 150,
                        "overlayMonitorIndex": "2",
                        "overlayOpacityRevision": 0,
                    },
                    f,
                )

            with patch("src.config.config.get_config_path", return_value=user_config_path), patch(
                "src.config.config.open_about",
            ):
                config = config_module.Config()

            self.assertEqual(config.hotkey, "ctrl+x")
            self.assertEqual(config.overlay_y_percent, 100)
            self.assertEqual(config.overlay_monitor_index, 2)
            self.assertEqual(config.opacity, config_module.DEFAULT_OPACITY)
            self.assertEqual(
                config.overlay_opacity_revision,
                config_module.OVERLAY_OPACITY_REVISION,
            )
            self.assertFalse(os.path.exists(f"{user_config_path}.tmp"))

            with open(user_config_path, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
            self.assertEqual(saved_config["overlayYPercent"], 100)
            self.assertEqual(saved_config["overlayMonitorIndex"], 2)
            self.assertEqual(
                saved_config["overlayOpacityRevision"],
                config_module.OVERLAY_OPACITY_REVISION,
            )

    def test_config_discards_invalid_monitor_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            user_config_path = os.path.join(temp_dir, "config.json")
            with open(user_config_path, "w", encoding="utf-8") as f:
                json.dump({"overlayMonitorIndex": -1}, f)

            with patch("src.config.config.get_config_path", return_value=user_config_path), patch(
                "src.config.config.open_about",
            ):
                config = config_module.Config()

            self.assertIsNone(config.overlay_monitor_index)


if __name__ == "__main__":
    unittest.main()
