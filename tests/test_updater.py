import unittest
import tempfile
import os
from tools.self_updater import SelfUpdaterTools


class TestSelfUpdaterTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.updater = SelfUpdaterTools(self.temp_dir.name)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def test_install_invalid_mcp_package_name(self):
        res = self.updater.install_mcp_package("")
        self.assertEqual(res["status"], "error")
        self.assertIn("Debe especificar el nombre", res["message"])


if __name__ == "__main__":
    unittest.main()
