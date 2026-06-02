import unittest
from unittest.mock import Mock, patch

import requests

from src.util import update_util


class UpdateUtilTest(unittest.TestCase):
    def _response(self, release_data):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = release_data
        return response

    def test_update_available_when_release_has_new_tag_and_installer(self):
        release_data = {
            "tag_name": "v9.9.9",
            "assets": [{"name": "CatLockSetup.exe"}],
            "draft": False,
            "prerelease": False,
        }

        with patch("src.util.update_util.requests.get", return_value=self._response(release_data)):
            self.assertTrue(update_util.is_update_available())

    def test_no_update_for_current_version(self):
        release_data = {
            "tag_name": update_util.VERSION,
            "assets": [{"name": "CatLockSetup.exe"}],
        }

        with patch("src.util.update_util.requests.get", return_value=self._response(release_data)):
            self.assertFalse(update_util.is_update_available())

    def test_no_update_without_installer_asset(self):
        release_data = {
            "tag_name": "v9.9.9",
            "assets": [{"name": "CatLock.zip"}],
        }

        with patch("src.util.update_util.requests.get", return_value=self._response(release_data)):
            self.assertFalse(update_util.is_update_available())

    def test_no_update_for_prerelease_or_request_failure(self):
        release_data = {
            "tag_name": "v9.9.9",
            "assets": [{"name": "CatLockSetup.exe"}],
            "prerelease": True,
        }

        with patch("src.util.update_util.requests.get", return_value=self._response(release_data)):
            self.assertFalse(update_util.is_update_available())

        with patch(
            "src.util.update_util.requests.get",
            side_effect=requests.exceptions.RequestException("offline"),
        ):
            self.assertFalse(update_util.is_update_available())


if __name__ == "__main__":
    unittest.main()
