import os
import sys
import subprocess
import shutil
from typing import Dict, Any, List

class SelfUpdaterTools:
    """
    Herramientas de Auto-Mantenimiento, Actualizaciones y Gestión Dinámica de MCP / Tools.
    Permite al agente revisar actualizaciones en GitHub, instalar dependencias y actualizar
    sus propios componentes o MCPs instalados en la USB.
    """

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def check_git_updates(self) -> Dict[str, Any]:
        """
        Consulta si hay actualizaciones o commits pendientes en el repositorio de GitHub.
        """
        try:
            # git fetch silencioso
            subprocess.run(["git", "fetch"], cwd=self.root_dir, capture_output=True, text=True, check=True)
            status = subprocess.run(["git", "status", "-uno"], cwd=self.root_dir, capture_output=True, text=True)
            
            behind = "behind" in status.stdout
            return {
                "status": "success",
                "updates_available": behind,
                "git_output": status.stdout.strip()
            }
        except Exception as e:
            return {"status": "error", "message": f"No se pudo consultar Git: {str(e)}"}

    def apply_git_update(self) -> Dict[str, Any]:
        """
        Descarga e instala las últimas actualizaciones del código del agente desde GitHub (git pull).
        """
        try:
            pull_res = subprocess.run(["git", "pull"], cwd=self.root_dir, capture_output=True, text=True)
            if pull_res.returncode == 0:
                # Re-instalar dependencias en caso de cambios en requirements.txt
                venv_pip = os.path.join(self.root_dir, ".venv", "Scripts", "pip.exe") if sys.platform == "win32" else os.path.join(self.root_dir, ".venv", "bin", "pip")
                if os.path.exists(venv_pip):
                    subprocess.run([venv_pip, "install", "-r", "requirements.txt"], cwd=self.root_dir, capture_output=True)
                
                return {"status": "success", "message": "Actualización de código y dependencias completada correctamente."}
            else:
                return {"status": "failed", "message": pull_res.stderr.strip()}
        except Exception as e:
            return {"status": "error", "message": f"Error aplicando actualización: {str(e)}"}

    def install_mcp_package(self, package_name: str) -> Dict[str, Any]:
        """
        Instala o actualiza un servidor o paquete MCP vía npx o pip (ej: '@modelcontextprotocol/server-github').
        """
        if not package_name:
            return {"status": "error", "message": "Debe especificar el nombre del paquete MCP."}

        try:
            if package_name.startswith("pip:") or package_name.startswith("py:"):
                clean_pkg = package_name.split(":", 1)[1]
                venv_pip = os.path.join(self.root_dir, ".venv", "Scripts", "pip.exe") if sys.platform == "win32" else os.path.join(self.root_dir, ".venv", "bin", "pip")
                cmd = [venv_pip, "install", clean_pkg]
            else:
                npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
                cmd = [npm_cmd, "install", "-g", package_name]

            res = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)
            return {
                "status": "success" if res.returncode == 0 else "failed",
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        except Exception as e:
            return {"status": "error", "message": f"Error instalando paquete MCP '{package_name}': {str(e)}"}
