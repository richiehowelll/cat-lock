import sys
import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

sys.modules.setdefault("keyboard", SimpleNamespace())
sys.modules.setdefault(
    "plyer",
    SimpleNamespace(notification=SimpleNamespace(notify=lambda **kwargs: None)),
)

from src.keyboard_controller import keyboard_lock_controller as lock_module


class KeyboardLockControllerTest(unittest.TestCase):
    def test_reserve_lock_request_rejects_duplicate_pending_request(self):
        controller = lock_module.KeyboardLockController(lambda: True)

        self.assertTrue(controller.reserve_lock_request())
        self.assertFalse(controller.reserve_lock_request())

    def test_lock_and_unlock_keyboard_updates_state_and_keys(self):
        controller = lock_module.KeyboardLockController(lambda: True)

        with patch("src.keyboard_controller.keyboard_lock_controller.KEY_CODES_TO_BLOCK", range(3)), patch(
            "src.keyboard_controller.keyboard_lock_controller.keyboard",
        ) as keyboard_mock, patch(
            "src.keyboard_controller.keyboard_lock_controller.send_notification_in_thread"
        ) as notify_mock:
            controller.lock_keyboard()

            self.assertTrue(controller.is_locked)
            self.assertEqual(controller.blocked_keys, {0, 1, 2})
            keyboard_mock.block_key.assert_has_calls([call(0), call(1), call(2)])
            notify_mock.assert_called_once_with(True)

            controller.unlock_keyboard()

            self.assertFalse(controller.is_locked)
            self.assertFalse(controller.lock_request_pending)
            self.assertEqual(controller.blocked_keys, set())
            keyboard_mock.unblock_key.assert_has_calls([call(0), call(1), call(2)], any_order=True)
            keyboard_mock.stash_state.assert_called_once()

    def test_lock_failure_unblocks_partial_keys_and_resets_state(self):
        controller = lock_module.KeyboardLockController(lambda: True)

        with patch("src.keyboard_controller.keyboard_lock_controller.KEY_CODES_TO_BLOCK", range(3)), patch(
            "src.keyboard_controller.keyboard_lock_controller.keyboard",
        ) as keyboard_mock, patch(
            "src.keyboard_controller.keyboard_lock_controller.send_notification_in_thread"
        ) as notify_mock:
            keyboard_mock.block_key.side_effect = [None, RuntimeError("failed")]

            with self.assertRaises(RuntimeError):
                controller.lock_keyboard()

            keyboard_mock.unblock_key.assert_called_once_with(0)
            self.assertFalse(controller.is_locked)
            self.assertFalse(controller.lock_request_pending)
            self.assertEqual(controller.blocked_keys, set())
            notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
