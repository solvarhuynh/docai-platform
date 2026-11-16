"""
Kiểm tra cấu hình API tối thiểu.
"""

import unittest
from docai.shared.config import Settings, settings


class TestConfig(unittest.TestCase):
    """
    Kiểm tra cấu hình API.
    """

    def test_settings_instance(self):
        self.assertIsInstance(settings, Settings)

    def test_api_defaults(self):
        self.assertEqual(settings.api_title, "DocAI")
        self.assertTrue(settings.api_version)


if __name__ == "__main__":
    unittest.main()
