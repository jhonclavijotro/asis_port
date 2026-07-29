import unittest
from tools.system_terminal import SystemTerminalTools


class TestSystemTerminalTools(unittest.TestCase):

    def setUp(self):
        self.terminal = SystemTerminalTools(timeout_seconds=5)

    def test_execute_echo_command(self):
        res = self.terminal.execute_command("echo Hola Asistente")
        self.assertEqual(res["status"], "success")
        self.assertIn("Hola Asistente", res["stdout"])

    def test_forbidden_command_blocked(self):
        res = self.terminal.execute_command("rm -rf /")
        self.assertEqual(res["status"], "error")
        self.assertIn("bloqueado por políticas de seguridad", res["message"])


if __name__ == "__main__":
    unittest.main()
