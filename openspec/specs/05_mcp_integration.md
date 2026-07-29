# OpenSpec Architecture: MCP Client & Server Architecture

## 1. Integración de MCP (Model Context Protocol) en el Asistente Portable

¡Sí, es totalmente posible y muy potente integrar **MCP**!

Integrar el estándar MCP en tu asistente portable ofrece dos grandes ventajas:
1. **Cliente MCP (MCP Client)**: Tu agente puede conectarse a cualquier servidor MCP externo o local (ej. servidores MCP de GitHub, Google Maps, SQLite, Brave Search, etc.) simplemente registrando la URL o el comando STDIO en tu archivo `config.yaml` o en el Vault.
2. **Servidor MCP Interno (MCP Server Provider)**: Tu propio asistente portable puede exponer sus herramientas portables (Bóveda de llaves, Calendario, Memoria) como un **servidor MCP** via STDIO o SSE. Esto significa que **puedes conectar tu disco USB a herramientas como Claude Desktop, Antigravity, Cursor o VSCode** y usar tus herramientas portables directamente en esos entornos.

---

## 2. Arquitectura propuesta para MCP Client/Server

```text
[ Portable USB Drive ]
┌───────────────────────────────────────────────────────────┐
│  Core Agent / Launcher                                    │
│  ┌───────────────────┐        ┌────────────────────────┐  │
│  │   MCP Client      │ ◄────► │ Portable MCP Server    │  │
│  └────────┬──────────┘        └───────────┬────────────┘  │
└───────────┼───────────────────────────────┼───────────────┘
            │ (stdio/sse)                   │ (stdio/sse)
            ▼                               ▼
    [ External MCP Servers ]       [ External LLM Clients ]
    - Brave Search MCP             - Claude Desktop / Cursor
    - GitHub MCP                   - Web Interfaces / Terminals
    - Local Filesystem MCP
```

---

## 3. Servidores MCP Útiles para Incluir / Soportar Out-of-the-Box

1. **`mcp-server-fetch` / `mcp-server-web`**: Para lectura y extracción rápida de contenido web en Markdown.
2. **`mcp-server-sqlite`**: Para interactuar directamente con tu base de datos de memoria u otras bases de datos SQLite en el disco portable.
3. **`mcp-server-obsidian` / `mcp-server-filesystem`**: Para editar notas en Markdown locales en el disco portable.
4. **`mcp-server-google-workspace`**: Para integración estandarizada con Gmail y Google Calendar.

---

## 4. Implementación Técnica en el Proyecto

Añadiremos un módulo dedicado: `core/mcp_client.py` usando la librería oficial de Python `mcp` (`pip install mcp`).

```python
# Ejemplo conceptual de cliente MCP en core/mcp_client.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPManager:
    """Gestiona conexiones dinámicas a servidores MCP desde la USB/Disco Portable."""
    def __init__(self):
        self.sessions = {}

    async def connect_stdio(self, server_name: str, command: str, args: list):
        server_params = StdioServerParameters(command=command, args=args)
        # Conexión asíncrona al servidor MCP
        # Transforma las herramientas devueltas por MCP a herramientas consumibles por tu Agent Loop
```

---

## 5. Actualización en el Roadmap (OpenSpec)

Hemos añadido la especificación [openspec/specs/05_mcp_integration.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/05_mcp_integration.md) para reflejar:
- Capacidad del Agente para consumir servidores MCP (stdio & sse).
- Exposición opcional del Asistente Portable como Servidor MCP.
