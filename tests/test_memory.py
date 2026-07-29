import os
import unittest
import tempfile
from core.memory import MemoryManager


class TestMemoryManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_memory.db")
        self.memory = MemoryManager(self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass


    def test_chat_history(self):
        session_id = "session_001"
        self.memory.add_chat_message(session_id, "user", "Hola Asistente")
        self.memory.add_chat_message(session_id, "assistant", "¡Hola! ¿En qué puedo ayudarte?")

        history = self.memory.get_chat_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["content"], "¡Hola! ¿En qué puedo ayudarte?")

    def test_semantic_memory(self):
        self.memory.store_semantic_fact(
            category="user_preferences",
            key_concept="language",
            content="El usuario prefiere respuestas en español.",
            tags=["idioma", "preferencias"]
        )

        results = self.memory.search_semantic_memory("español")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["key_concept"], "language")

    def test_system_manual_injection(self):
        manual = [
            {
                "tool_name": "google_calendar",
                "description": "Gestiona eventos del calendario.",
                "usage_guide": "Llama a esta herramienta pasando start_date y end_date."
            }
        ]
        self.memory.inject_system_manual(manual)

        guide = self.memory.get_tool_guide("google_calendar")
        self.assertIsNotNone(guide)
        self.assertEqual(guide["description"], "Gestiona eventos del calendario.")


if __name__ == "__main__":
    unittest.main()
