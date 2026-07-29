import os
import sys
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from core.vault import VaultManager
from core.memory import MemoryManager
from core.agent import PortableAgent
from tools.google_workspace import GoogleWorkspaceTools
from tools.system_terminal import SystemTerminalTools
from tools.self_updater import SelfUpdaterTools



console = Console()

def main():
    console.print(Panel.fit("[bold cyan]🤖 ASISTENTE PERSONAL PORTABLE[/bold cyan]\n[dim]Estructura agéntica autónoma desde almacenamiento USB/Portable[/dim]", border_style="cyan"))

    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "storage"))
    os.makedirs(storage_dir, exist_ok=True)

    vault_path = os.path.join(storage_dir, "vault.enc")
    db_path = os.path.join(storage_dir, "memory.db")

    # 1. Autenticación con Bóveda Segura
    try:
        master_passphrase = getpass.getpass("🔑 Ingrese su Contraseña Maestra de la Bóveda USB: ")
    except Exception:
        master_passphrase = Prompt.ask("🔑 Ingrese su Contraseña Maestra de la Bóveda USB", password=True)

    if not master_passphrase:
        console.print("[bold red]La contraseña no puede estar vacía. Abortando.[/bold red]")
        sys.exit(1)


    try:
        vault = VaultManager(vault_path, master_passphrase)
        console.print("[bold green]✔ Bóveda desprotegida correctamente (AES-256).[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Error de Bóveda:[/bold red] {e}")
        sys.exit(1)

    # 2. Inicialización de Memoria y Agente
    memory = MemoryManager(db_path)
    agent = PortableAgent(vault, memory)

    # 3. Registro de Herramientas
    google_tools = GoogleWorkspaceTools(vault)
    terminal_tools = SystemTerminalTools()
    updater_tools = SelfUpdaterTools(root_dir=os.path.dirname(__file__))

    agent.register_tool(
        name="search_emails",
        description="Busca correos en Gmail por asunto o palabras clave",
        func=google_tools.search_emails,
        usage_guide="Buscar correos cuando el usuario pregunte por mensajes o email."
    )
    agent.register_tool(
        name="get_upcoming_events",
        description="Obtiene próximos eventos agendados en Google Calendar",
        func=google_tools.get_upcoming_events,
        usage_guide="Obtener calendario cuando el usuario pregunte por reuniones o agenda."
    )
    agent.register_tool(
        name="execute_command",
        description="Ejecuta comandos de consola de terminal (PowerShell, Bash, SSH)",
        func=terminal_tools.execute_command,
        usage_guide="Ejecutar comandos en la consola del sistema (ej: ping, ssh, dir, ls, git)."
    )
    agent.register_tool(
        name="check_updates",
        description="Consulta si existen nuevas actualizaciones del agente en GitHub",
        func=updater_tools.check_git_updates,
        usage_guide="Comprobar actualizaciones de código desde GitHub."
    )
    agent.register_tool(
        name="install_mcp_package",
        description="Instala un servidor o paquete MCP dinámicamente vía npm o pip",
        func=updater_tools.install_mcp_package,
        usage_guide="Instalar nuevos paquetes MCP o dependencias."
    )

    console.print("[dim]Herramientas registradas: Gmail, Google Calendar, Terminal, Auto-Updater/MCP, Memoria.[/dim]")


    console.print("[bold yellow]Comandos especiales: '/config' (gestionar llaves/modelos) | 'salir' / 'exit' (finalizar)[/bold yellow]\n")

    # 4. Bucle interactivo
    session_id = "portable_cli_session"
    while True:
        try:
            user_prompt = Prompt.ask("[bold green]Tú[/bold green]")
            if user_prompt.strip().lower() in ["salir", "exit", "quit"]:
                console.print("[bold cyan]👋 ¡Hasta luego! Tus datos permanecen encriptados en la USB.[/bold cyan]")
                break
            
            if user_prompt.strip().lower() == "/config":
                console.print("\n[bold yellow]⚙️ CONFIGURACIÓN DE LA BÓVEDA PORTABLE[/bold yellow]")
                console.print("1. Configurar GEMINI_API_KEY")
                console.print("2. Configurar OPENAI_API_KEY")
                console.print("3. Cambiar Modelo por Defecto (ej: gemini/gemini-1.5-flash, gpt-4o, etc.)")
                console.print("4. Volver al Chat")
                
                opcion = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4"], default="4")
                if opcion == "1":
                    key = Prompt.ask("Pega tu GEMINI_API_KEY", password=True)
                    vault.set_secret("GEMINI_API_KEY", key)
                    console.print("[bold green]✔ GEMINI_API_KEY guardada encriptada en la USB.[/bold green]\n")
                elif opcion == "2":
                    key = Prompt.ask("Pega tu OPENAI_API_KEY", password=True)
                    vault.set_secret("OPENAI_API_KEY", key)
                    console.print("[bold green]✔ OPENAI_API_KEY guardada encriptada en la USB.[/bold green]\n")
                elif opcion == "3":
                    actual = vault.get_secret("DEFAULT_MODEL", "gemini/gemini-1.5-flash")
                    nuevo_modelo = Prompt.ask(f"Modelo actual: [cyan]{actual}[/cyan]. Ingrese nuevo modelo", default=actual)
                    vault.set_secret("DEFAULT_MODEL", nuevo_modelo)
                    console.print(f"[bold green]✔ Modelo cambiado a: {nuevo_modelo}[/bold green]\n")
                continue

            if not user_prompt.strip():
                continue

            response = agent.run(user_prompt, session_id=session_id)
            console.print(f"\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold cyan]👋 Sesión finalizada.[/bold cyan]")
            break


if __name__ == "__main__":
    main()
