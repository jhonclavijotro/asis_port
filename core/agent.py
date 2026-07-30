import os
import json
from typing import List, Dict, Any, Callable
from core.vault import VaultManager
from core.memory import MemoryManager



class PortableAgent:
    """
    Orquestador Agéntico ReAct Ligero y Portable.
    Gestión dinámica de herramientas, memoria episódica/semántica y fallback inteligente.
    """

    def __init__(self, vault: VaultManager, memory: MemoryManager):
        self.vault = vault
        self.memory = memory
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: Dict[str, str] = {}
        self._register_default_manual()

    def register_tool(self, name: str, description: str, func: Callable, usage_guide: str = "") -> None:
        """Registra una herramienta disponible para el agente."""
        self.tools[name] = func
        self.tool_descriptions[name] = description
        if usage_guide:
            self.memory.inject_system_manual([
                {"tool_name": name, "description": description, "usage_guide": usage_guide}
            ])

    def _register_default_manual(self) -> None:
        """Inicializa las instrucciones del manual en la memoria persistente."""
        manual = [
            {
                "tool_name": "system_help",
                "description": "Ofrece información de ayuda sobre el asistente y sus capacidades.",
                "usage_guide": "Invocado cuando el usuario pregunta qué puede hacer el asistente."
            }
        ]
        self.memory.inject_system_manual(manual)

    def run(self, user_input: str, session_id: str = "default_session") -> str:
        """
        Ejecuta el ciclo agéntico procesando el prompt del usuario.
        """
        # 1. Guardar mensaje del usuario en memoria episódica
        self.memory.add_chat_message(session_id, "user", user_input)

        # 2. Consultar memoria semántica previa por si hay contexto relevante
        context_facts = self.memory.search_semantic_memory(user_input)
        context_str = ""
        if context_facts:
            context_str = "\n[Contexto Recordado]: " + "; ".join([f"{f['key_concept']}: {f['content']}" for f in context_facts])

        # 3. Verificar si el prompt requiere alguna herramienta explícita
        input_lower = user_input.lower()
        tool_output = None

        if ("correo" in input_lower or "email" in input_lower or "gmail" in input_lower) and "search_emails" in self.tools:
            tool_output = self.tools["search_emails"](query=user_input)
        elif ("calendario" in input_lower or "evento" in input_lower or "reunión" in input_lower) and "get_upcoming_events" in self.tools:
            tool_output = self.tools["get_upcoming_events"]()
        elif "ayuda" in input_lower or "herramientas" in input_lower:
            tools_list = ", ".join(self.tools.keys())
            response = f"🤖 **Asistente Portable Activo**\nHerramientas disponibles: [{tools_list}].\nTodas tus claves están cifradas en la Bóveda USB.{context_str}"
            self.memory.add_chat_message(session_id, "assistant", response)
            return response

        # 4. Construir llamada al LLM o ejecutar herramienta
        if tool_output:
            response = f"🤖 **Resultado de Herramienta**:\n```json\n{json.dumps(tool_output, indent=2, ensure_ascii=False)}\n```\n{context_str}"
        else:
            # Obtener proveedor, api_base y llaves configuradas en la bóveda
            provider_model = self.vault.get_secret("DEFAULT_MODEL", "gemini/gemini-1.5-flash")
            api_base = self.vault.get_secret("CUSTOM_API_BASE", None)  # Para Ollama/Raspberry Pi o vLLM
            gemini_key = self.vault.get_secret("GEMINI_API_KEY")
            openai_key = self.vault.get_secret("OPENAI_API_KEY")
            anthropic_key = self.vault.get_secret("ANTHROPIC_API_KEY")

            # Si el modelo empieza por gemini- sin prefijo 'gemini/', agregarlo para Google AI Studio API Keys
            if (provider_model.startswith("gemini-") or "gemini" in provider_model.lower()) and not provider_model.startswith("gemini/"):
                provider_model = f"gemini/{provider_model}"

            # Configurar variables de entorno si existen en el Vault
            if gemini_key:
                os.environ["GEMINI_API_KEY"] = gemini_key
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key

            # Cargar System Prompt Maestro
            system_prompt = (
                "Eres un asistente personal agéntico portable ejecutable desde USB. "
                "Sé preciso, útil y seguro. "
                f"{context_str}"
            )

            try:
                import litellm
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
                
                kwargs = {"model": provider_model, "messages": messages}
                if api_base:
                    kwargs["api_base"] = api_base

                completion = litellm.completion(**kwargs)
                response = f"🤖 [{provider_model}]: {completion.choices[0].message.content}"
            except Exception as e:
                response = (
                    f"🤖 **No se pudo conectar al modelo '{provider_model}'**: {e}\n"
                    f"💡 *Sugerencia*: Si utilizas Gemini de Google AI Studio, asegúrate de haber configurado tu GEMINI_API_KEY en '/config'."
                )



        # 5. Guardar respuesta del asistente en memoria episódica
        self.memory.add_chat_message(session_id, "assistant", response)
        return response

