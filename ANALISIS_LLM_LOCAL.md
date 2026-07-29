# Análisis Técnico: LLMs Locales, Raspberry Pi 5 y System Prompt Maestro

---

## 1. LLM Local Expuesto vía Web para Agente Independiente
**¿Es posible?** Sí, es 100% posible y es uno de los casos de uso más avanzados para privacidad y soberanía de datos.

### ¿Cómo funciona?
1. **Ejecución Local del LLM**: Utilizas un servidor local de inferencia como **Ollama**, **vLLM** o **LM Studio**.
2. **Exposición a Internet Segura**:
   - Vía túnel seguro como **Cloudflare Tunnels (cloudflared)**, **ngrok**, o **Tailscale Funnel**.
   - Esto te genera una URL pública HTTPS (ej. `https://mi-llm-privado.trycloudflare.com/v1`).
3. **Conexión en tu Asistente Portable**:
   - Gracias a que nuestro agente utiliza `litellm`, simplemente registras en la Bóveda USB:
     - `DEFAULT_MODEL` = `ollama/llama3.2` (o `openai/custom-model`)
     - `api_base` = `https://mi-llm-privado.trycloudflare.com/v1`
   - **Resultado**: Tu asistente portable desde cualquier terminal del mundo enviará sus preguntas a tu propio servidor casero/servidor local sin pagar APIs a terceros.

---

## 2. Pruebas con Modelo Pequeño en Raspberry Pi 5 (8GB RAM)
**¿Es posible?** Sí, la Raspberry Pi 5 es una excelente plataforma para esto.

### Modelos Recomendados para Raspberry Pi 5:
- **Llama 3.2 1B / 3B** (Cuantizado a 4-bit / Q4_K_M): Ocupa ~2.5 GB de RAM. Corre a ~10-15 tokens/segundo.
- **Qwen 2.5 1.5B / 3B**: Excelente para seguimiento de instrucciones y llamadas a herramientas (function calling).
- **Phi-3 Mini 3.8B** (Microsoft): Gran razonamiento en tamaño reducido.

### Configuración en la Raspberry Pi 5:
```bash
# 1. Instalar Ollama en la Raspberry Pi 5
curl -fsSL https://ollama.com/install.sh | sh

# 2. Descargar un modelo ligero optimizado para agentes
ollama run llama3.2:3b

# 3. Exponer Ollama a tu red local o internet
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

---

## 3. Prompt Maestro (System Prompt) para el Agente
**¿Es posible y recomendable?** Sí, es **crucial**. El Prompt Maestro define la personalidad, las reglas de seguridad, el tono de respuesta y la guía estricta de cuándo usar herramientas.

### Estructura de un Prompt Maestro Recomendado

```text
SYSTEM_PROMPT = """
Eres Jarvis-Portable, un asistente personal agéntico altamente capaz, empático y profesional.
Tu almacenamiento, memoria y credenciales viven encriptados en la unidad USB del usuario.

## Reglas de Comportamiento y Tono:
1. Tono: Conciso, directo y profesional. Responde en el idioma que utilice el usuario.
2. Privacidad: Jamás expongas claves API, tokens de sesión o datos sensibles en el chat.
3. Uso de Herramientas:
   - Antes de responder dudas sobre agenda, consulta la herramienta 'get_upcoming_events'.
   - Antes de responder dudas sobre correos, consulta la herramienta 'search_emails'.
   - Si no tienes la información, utiliza tu memoria semántica o declara que no la posees.
4. Memoria: Incorpora el contexto recordado en tus respuestas sin sonar repetitivo.
"""
```

---

## 🚀 Hoja de Ruta para Integrar estas 3 Ideas en el Proyecto

1. **Añadir el Prompt Maestro en `core/agent.py`**: Personalizable desde un archivo `prompts/system_prompt.txt` dentro de la USB.
2. **Sustituir/Añadir `api_base` en la Bóveda**: Permitir conectar endpoints personalizados de Ollama / LM Studio local desde el menú `/config`.
3. **Registro en `FUTURO.md`**: Guardar la arquitectura de Raspberry Pi 5 + Cloudflare Tunnels para pruebas de campo.
