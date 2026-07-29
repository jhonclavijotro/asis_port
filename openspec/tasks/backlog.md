# Backlog de Tareas (MVP Phase 1)

## High Priority (Fase 1 - Core MVP)
- [ ] **[Spec 01] Implementar VaultManager (`core/vault.py`)**:
  - Encriptación Fernet / AES-256 con contraseña maestra derivada mediante PBKDF2HMAC.
  - Métodos `set_secret()`, `get_secret()`, `list_secrets()`.
  - Persistencia en `storage/vault.enc`.

- [ ] **[Spec 02] Implementar Memory Engine (`core/memory.py`)**:
  - `EpisodicMemory`: Persistencia de chat en SQLite `storage/history.db`.
  - `SemanticMemory`: Almacenamiento vectorial simple para preferencias y notas de contexto.

- [ ] **[Spec 03] Implementar Google Workspace Integration (`tools/google_workspace.py`)**:
  - Autenticación OAuth 2.0 almacenando tokens en el Vault.
  - Gmail API: `search_emails()`, `send_email()`.
  - Google Calendar API: `get_upcoming_events()`, `create_event()`.

- [ ] **[Spec 04] Orquestador de Agente ReAct (`core/agent.py`)**:
  - Registro dinámico de herramientas.
  - Integración con LLM vía LiteLLM / LangChain / Native SDK.

- [ ] **[CLI Launcher] Crear lanzador CLI interactivo (`launcher.py`)**:
  - Solicitar contraseña maestra al inicio.
  - Cargar boveda y registrar herramientas.
  - Bucle de chat interactivo con `rich`.
