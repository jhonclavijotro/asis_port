# Registro de Futuras Mejoras e Ideas (FUTURO.md)

Este documento registra ideas, mejoras arquitectónicas y nuevas capacidades que surjan durante el desarrollo del Asistente Portable para ser implementadas en versiones posteriores.

---

## 💡 Ideas y Mejoras Futuras

### 1. Manual de Uso Autoinyectado en Memoria Persistente
- **Descripción**: Al inicializar la memoria persistente por primera vez (SQLite + VectorStore), inyectar un manual de uso completo del asistente.
- **Objetivo**: Permitir que el agente consulte de forma autónoma su propio manual para saber cuándo y cómo invocar cada herramienta (Tools y MCPs), comprender límites de uso y ofrecer ayuda detallada al usuario ante dudas.

### 2. Auto-evaluación y Optimización de Prompts de Herramientas
- **Descripción**: Permitir que el agente registre métricas internas sobre qué herramientas fallan o entregan respuestas ambiguas para auto-sugerir mejoras en sus prompts del sistema.

### 3. Sincronización Remota Encriptada (Opcional)
- **Descripción**: Permitir respaldar el `storage/` encriptado hacia un bucket de Cloud Storage (GCS) o Dropbox si el disco USB se extravía, descifrado únicamente con la Contraseña Maestra.
