import unittest
import tempfile
import os
from core.vault import VaultManager
from core.memory import MemoryManager
from core.agent import PortableAgent


class TestPortableAgent(unittest.TestCase):

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

    def test_agent_run_help(self):
        response = self.agent.run("ayuda")
        self.assertIn("Asistente Portable Activo", response)

    def test_agent_uses_registered_tool(self):
        def dummy_tool(query: str):
            return {"dummy_result": query}

        self.agent.register_tool("search_emails", "Busca correos", dummy_tool)
        response = self.agent.run("Buscar correos sobre proyecto")
        self.assertIn("dummy_result", response)


if __name__ == "__main__":
    unittest.main()
