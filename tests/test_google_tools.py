import unittest
import tempfile
import os
from core.vault import VaultManager
from tools.google_workspace import GoogleWorkspaceTools


class TestGoogleWorkspaceTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = os.path.join(self.temp_dir.name, "vault.enc")
        self.vault = VaultManager(self.vault_path, "Pass123!")
        self.tools = GoogleWorkspaceTools(self.vault)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def test_tools_require_oauth_token(self):
        # Sin token en la bóveda, debe informar error
        res = self.tools.search_emails("test")
        self.assertIn("error", res[0])

        # Agregamos token simulado
        self.vault.set_secret("GOOGLE_OAUTH_TOKEN", "fake_token_123")
        res_with_token = self.tools.search_emails("test")
        self.assertEqual(res_with_token[0]["id"], "msg_001")


if __name__ == "__main__":
    unittest.main()
