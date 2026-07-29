# OpenSpec Project Specification: Portable AI Assistant

## Metadata
- **Project**: Portable AI Assistant
- **Version**: 0.1.0-alpha
- **Author**: Antigravity & User
- **Target OS**: Cross-Platform (Windows, Linux, macOS)
- **Execution Mode**: Standalone Portable Storage Execution (USB / External SSD)

---

## 1. Vision & Core Philosophy
Build a zero-footprint, self-contained AI Personal Assistant that can run off a portable USB drive or external SSD on any machine with internet access and Python. The assistant manages calendar, email, long-term memory, and local secret vault without leaving sensitive unencrypted credentials on host machines.

---

## 2. Selected Core Modules (MVP Phase 1)
1. **Portable Vault Manager (`core/vault.py`)**:
   - AES-256 (Fernet) encryption for API keys (OpenAI, Gemini, Anthropic, etc.) & OAuth tokens.
   - Decryption via Master Passphrase at session startup.
2. **Google Workspace Tools (`tools/google_workspace.py`)**:
   - Gmail API: Email search, thread reading, sending emails.
   - Google Calendar API: Event querying, event creation.
   - Token storage inside the encrypted portable vault.
3. **Long-Term Memory Engine (`core/memory.py`)**:
   - SQLite database for episodic conversation history.
   - Vector database (LanceDB/Chroma) for semantic memory and preference retrieval.
4. **Agent Orchestrator (`core/agent.py`)**:
   - ReAct loop supporting dynamic tool calling and structured response generation.
5. **MCP Client & Server Engine (`core/mcp_manager.py`)**:
   - Soporte para conectar el agente a servidores MCP externos (Brave Search, GitHub, SQLite, etc.).
   - Capacidad de exponer tu asistente como un servidor MCP para usarlo en Claude Desktop / Cursor.

---

## 3. Specifications Index
- [01_vault_security.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/01_vault_security.md)
- [02_agent_core.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/02_agent_core.md)
- [03_google_tools.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/03_google_tools.md)
- [04_memory_engine.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/04_memory_engine.md)
- [05_mcp_integration.md](file:///d:/CODIGOS/Asistente_portable/openspec/specs/05_mcp_integration.md)

