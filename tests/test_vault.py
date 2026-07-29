import os
import unittest
import tempfile
from core.vault import VaultManager


class TestVaultManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = os.path.join(self.temp_dir.name, "test_vault.enc")
        self.master_pass = "SuperSecretPassphrase123!"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_retrieve_secret(self):
        vault = VaultManager(self.vault_path, self.master_pass)
        vault.set_secret("OPENAI_API_KEY", "sk-test-key-12345")

        # Re-abrir bóveda con la misma clave
        vault2 = VaultManager(self.vault_path, self.master_pass)
        self.assertEqual(vault2.get_secret("OPENAI_API_KEY"), "sk-test-key-12345")

    def test_wrong_passphrase_raises_error(self):
        vault = VaultManager(self.vault_path, self.master_pass)
        vault.set_secret("GEMINI_API_KEY", "gemini-secret")

        # Intentar abrir con contraseña incorrecta debe fallar
        with self.assertRaises(ValueError):
            VaultManager(self.vault_path, "WrongPassword!")

    def test_delete_secret(self):
        vault = VaultManager(self.vault_path, self.master_pass)
        vault.set_secret("TEMP_TOKEN", "to-be-deleted")
        self.assertTrue(vault.delete_secret("TEMP_TOKEN"))

        vault2 = VaultManager(self.vault_path, self.master_pass)
        self.assertIsNone(vault2.get_secret("TEMP_TOKEN"))


if __name__ == "__main__":
    unittest.main()
