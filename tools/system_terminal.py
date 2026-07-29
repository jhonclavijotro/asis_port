import subprocess
import shlex
import os
import platform
from typing import Dict, Any

class SystemTerminalTools:
    """
    Herramientas de ejecución de comandos de consola del sistema para el Asistente Portable.
    Permite ejecutar comandos locales o remotos (ej: ssh) con controles de seguridad.
    """

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Ejecuta un comando de consola en el sistema hospedador y retorna la salida (stdout/stderr).
        """
        if not command or not command.strip():
            return {"status": "error", "message": "El comando no puede estar vacío."}

        # Evitar comandos destructivos accidentales de alto riesgo por seguridad básica
        forbidden = ["rm -rf /", "mkfs", "dd if=", "format c:"]
        for bad in forbidden:
            if bad in command.lower():
                return {"status": "error", "message": f"Comando bloqueado por políticas de seguridad: {command}"}

        try:
            is_windows = platform.system() == "Windows"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": f"El comando excedió el tiempo límite de {self.timeout_seconds} segundos."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al ejecutar comando: {str(e)}"
            }
