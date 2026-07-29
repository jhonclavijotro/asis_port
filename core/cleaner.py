import os
import shutil
import tempfile
import sys

class ZeroTraceCleaner:
    """
    Gestor de Limpieza Fantasma (Zero-Trace Mode).
    Limpia cachés, temporales del sistema hospedador y variables de entorno sensibles al salir.
    """

    @staticmethod
    def cleanup_env_vars():
        """Elimina variables de entorno de API Keys cargadas en la memoria RAM del sistema."""
        keys_to_remove = ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_OAUTH_TOKEN"]
        for key in keys_to_remove:
            if key in os.environ:
                del os.environ[key]

    @staticmethod
    def cleanup_temp_files():
        """Elimina archivos temporales residuales creados durante la sesión del asistente."""
        try:
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                if item.startswith("portable_agent_tmp_"):
                    full_path = os.path.join(temp_dir, item)
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path, ignore_errors=True)
        except Exception:
            pass

    @classmethod
    def full_zero_trace_exit(cls):
        """Ejecuta la secuencia completa de limpieza fantasma al cerrar sesión."""
        cls.cleanup_env_vars()
        cls.cleanup_temp_files()
