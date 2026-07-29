import unittest
import tempfile
import os
from core.vault import VaultManager
from core.memory import MemoryManager
from core.agent import PortableAgent
from core.cleaner import ZeroTraceCleaner
from core.workflows import WorkflowEngine


class TestAdvancedFeatures(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = os.path.join(self.temp_dir.name, "vault.enc")
        self.db_path = os.path.join(self.temp_dir.name, "memory.db")

        self.vault = VaultManager(self.vault_path, "Pass123!")
        self.memory = MemoryManager(self.db_path)
        self.agent = PortableAgent(self.vault, self.memory)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def test_panic_mode_destroys_vault(self):
        # Crear bóveda con contenido
        self.vault.set_secret("SECRET_KEY", "sensitive_val")
        self.assertTrue(os.path.exists(self.vault_path))

        # Intentar acceder con frase de pánico debe activar Kill-Switch
        with self.assertRaises(ValueError):
            VaultManager(self.vault_path, "PANIC_DESTROY")

        # La bóveda ya no debe existir físicamente
        self.assertFalse(os.path.exists(self.vault_path))

    def test_zero_trace_cleaner(self):
        os.environ["GEMINI_API_KEY"] = "fake_key"
        ZeroTraceCleaner.cleanup_env_vars()
        self.assertNotIn("GEMINI_API_KEY", os.environ)

    def test_workflow_engine(self):
        engine = WorkflowEngine(self.agent)
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {"name": "Step 1", "prompt": "ayuda"}
            ]
        }
        res = engine.execute_workflow_dict(workflow)
        self.assertEqual(len(res), 1)
        self.assertIn("Asistente Portable Activo", res[0]["result"])


if __name__ == "__main__":
    unittest.main()
