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

---

## 🎨 Propuestas Creativas e Innovadoras

### 4. USB "Kill-Switch" & Auto-Destrucción Panic Mode
- **Descripción**: Si se ingresa una contraseña de pánico o fallan 5 intentos consecutivos al desbloquear la Bóveda USB, el asistente puede sobrescribir con ceros (`shred`) el archivo `storage/vault.enc` para garantizar cero fuga de datos si la memoria USB se pierde.

### 5. Interfaz de Voz Offline / Portable (Whisper + Piper TTS)
- **Descripción**: Integrar transcriptor de voz `whisper.cpp` (ultra ligero en C++) y sintetizador `piper` para hablar con tu asistente por micrófono desde la USB sin depender de APIs de voz.

### 6. Sistema de Plantillas y Automatizaciones (Agent Workflows)
- **Descripción**: Crear un motor de Workflows (ej. "Morning Routine") donde el agente ejecute en secuencia:
  1. Revisar correos no leídos.
  2. Consultar la agenda del día en Google Calendar.
  3. Buscar el clima/noticias.
  4. Generar una nota de briefing diaria en Markdown.

### 7. "Zero-Trace Mode" (Modo Fantasma en Host)
- **Descripción**: Al cerrar la sesión, limpiar automáticamente la memoria caché de RAM, el historial de portapapeles y los registros temporales creados en la computadora donde te conectaste.

### 8. Web Dashboard Embebido en Localhost
- **Descripción**: Incluir un servidor FastAPI ultra-ligero que abra una interfaz gráfica futurista en el navegador local (`http://localhost:8000`) además del modo CLI de terminal.

