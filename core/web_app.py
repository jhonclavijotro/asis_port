import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict
from core.vault import VaultManager
from core.memory import MemoryManager
from core.agent import PortableAgent

app = FastAPI(title="Portable AI Assistant - Local Dashboard", version="1.0.0")

# Instancia global del agente cargado
agent_instance: Optional[PortableAgent] = None
vault_instance: Optional[VaultManager] = None

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "web_session"

class VaultInitRequest(BaseModel):
    master_passphrase: str

class ConfigUpdateRequest(BaseModel):
    gemini_key: Optional[str] = None
    openai_key: Optional[str] = None
    model_name: Optional[str] = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Asistente Portable - Dashboard Local</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --border-color: #1f2937;
            --accent-color: #06b6d4;
            --text-color: #f3f4f6;
            --user-msg-bg: #1e293b;
            --bot-msg-bg: #0f172a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); display: flex; height: 100vh; justify-content: center; align-items: center; }
        .container { width: 950px; height: 90vh; background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
        .header { padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: rgba(17,24,39,0.8); backdrop-filter: blur(10px); }
        .header h1 { font-size: 1.25rem; font-weight: 700; color: var(--accent-color); }
        .nav-btns { display: flex; gap: 10px; align-items: center; }
        .status-badge { font-size: 0.8rem; padding: 4px 12px; background: rgba(6,182,212,0.1); border: 1px solid var(--accent-color); border-radius: 20px; color: var(--accent-color); }
        
        .unlock-panel { padding: 40px; text-align: center; margin: auto; max-width: 400px; }
        .unlock-panel input, .config-panel input { width: 100%; padding: 12px; margin: 10px 0; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; font-size: 0.95rem; outline: none; }
        .btn { padding: 10px 20px; background: var(--accent-color); border: none; border-radius: 8px; color: #000; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn:hover { opacity: 0.9; }
        .btn-outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-color); }
        .btn-outline:hover { border-color: var(--accent-color); color: var(--accent-color); }
        
        .chat-panel { display: none; flex-direction: column; height: 100%; }
        .messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { padding: 14px 18px; border-radius: 12px; max-width: 80%; line-height: 1.5; font-size: 0.95rem; white-space: pre-wrap; }
        .message.user { align-self: flex-end; background: var(--user-msg-bg); border: 1px solid #334155; }
        .message.bot { align-self: flex-start; background: var(--bot-msg-bg); border: 1px solid var(--border-color); border-left: 4px solid var(--accent-color); }
        
        .input-area { padding: 16px; border-top: 1px solid var(--border-color); display: flex; gap: 12px; background: var(--card-bg); }
        .input-area input { flex: 1; padding: 14px; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; outline: none; font-size: 0.95rem; }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); justify-content: center; align-items: center; }
        .config-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 30px; width: 450px; }
        .config-card h2 { margin-bottom: 16px; font-size: 1.2rem; color: var(--accent-color); }
        .config-card label { font-size: 0.85rem; color: #9ca3af; margin-top: 8px; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Portable AI Assistant</h1>
            <div class="nav-btns">
                <span class="status-badge" id="status-text">Bóveda Bloqueada</span>
                <button class="btn btn-outline" id="config-btn" style="display:none;" onclick="openConfigModal()">⚙️ Ajustes / Keys</button>
            </div>
        </div>

        <!-- Pantalla de Desbloqueo -->
        <div class="unlock-panel" id="unlock-panel">
            <h2>🔐 Desbloquear Bóveda USB</h2>
            <p style="color: #9ca3af; font-size: 0.85rem; margin-top: 8px;">Ingrese su contraseña maestra para inicializar las herramientas agénticas.</p>
            <input type="password" id="master-pass" placeholder="Contraseña Maestra">
            <button class="btn" style="width: 100%;" onclick="unlockVault()">Desbloquear Bóveda</button>
            <p id="unlock-error" style="color: #ef4444; font-size: 0.85rem; margin-top: 12px; display: none;"></p>
        </div>

        <!-- Panel de Chat -->
        <div class="chat-panel" id="chat-panel">
            <div class="messages" id="messages"></div>
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Escribe tu mensaje o comando..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button class="btn" style="width: auto; padding: 0 24px;" onclick="sendMessage()">Enviar</button>
            </div>
        </div>
    </div>

    <!-- Modal de Configuración de Llaves y Modelo -->
    <div class="modal" id="config-modal">
        <div class="config-card">
            <h2>⚙️ Configurar Credenciales y Modelo</h2>
            <label>GEMINI_API_KEY</label>
            <input type="password" id="cfg-gemini" placeholder="Pega tu GEMINI_API_KEY de Google AI Studio">
            
            <label>OPENAI_API_KEY (Opcional)</label>
            <input type="password" id="cfg-openai" placeholder="Pega tu OPENAI_API_KEY">
            
            <label>Modelo por Defecto</label>
            <input type="text" id="cfg-model" placeholder="ej: gemini/gemini-1.5-flash, gpt-4o, etc.">
            
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn" style="flex: 1;" onclick="saveConfig()">Guardar en USB</button>
                <button class="btn btn-outline" style="flex: 1;" onclick="closeConfigModal()">Cancelar</button>
            </div>
            <p id="cfg-msg" style="font-size: 0.85rem; margin-top: 10px; display: none;"></p>
        </div>
    </div>

    <script>
        async function unlockVault() {
            const pass = document.getElementById('master-pass').value;
            const errEl = document.getElementById('unlock-error');
            errEl.style.display = 'none';

            try {
                const res = await fetch('/api/unlock', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({master_passphrase: pass})
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al desbloquear');

                document.getElementById('unlock-panel').style.display = 'none';
                document.getElementById('chat-panel').style.display = 'flex';
                document.getElementById('config-btn').style.display = 'inline-block';
                document.getElementById('status-text').innerText = 'Bóveda Desbloqueada (AES-256)';
                loadCurrentConfig();
            } catch (err) {
                errEl.innerText = err.message;
                errEl.style.display = 'block';
            }
        }

        async function loadCurrentConfig() {
            try {
                const res = await fetch('/api/config');
                const data = await res.json();
                if (data.status === 'success') {
                    document.getElementById('cfg-model').value = data.config.model_name || 'gemini/gemini-1.5-flash';
                }
            } catch (e) {}
        }

        function openConfigModal() {
            document.getElementById('config-modal').style.display = 'flex';
        }

        function closeConfigModal() {
            document.getElementById('config-modal').style.display = 'none';
        }

        async function saveConfig() {
            const gemini = document.getElementById('cfg-gemini').value;
            const openai = document.getElementById('cfg-openai').value;
            const model = document.getElementById('cfg-model').value;
            const msgEl = document.getElementById('cfg-msg');

            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gemini_key: gemini, openai_key: openai, model_name: model})
                });
                const data = await res.json();
                msgEl.style.color = '#10b981';
                msgEl.innerText = '✔ Configuración guardada encriptada en la USB';
                msgEl.style.display = 'block';
                setTimeout(closeConfigModal, 1200);
            } catch (err) {
                msgEl.style.color = '#ef4444';
                msgEl.innerText = 'Error al guardar';
                msgEl.style.display = 'block';
            }
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text) return;

            appendMessage('user', text);
            input.value = '';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await res.json();
                appendMessage('bot', data.response);
            } catch (err) {
                appendMessage('bot', '❌ Error al comunicarse con el asistente.');
            }
        }

        function appendMessage(sender, text) {
            const msgs = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.innerText = text;
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return HTML_TEMPLATE

@app.post("/api/unlock")
def unlock_vault(req: VaultInitRequest):
    global agent_instance, vault_instance
    try:
        storage_dir = os.path.abspath("storage")
        vault_path = os.path.join(storage_dir, "vault.enc")
        db_path = os.path.join(storage_dir, "memory.db")

        vault_instance = VaultManager(vault_path, req.master_passphrase)
        memory = MemoryManager(db_path)
        agent_instance = PortableAgent(vault_instance, memory)
        return {"status": "success", "message": "Bóveda USB desbloqueada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/config")
def get_config():
    global vault_instance
    if not vault_instance:
        raise HTTPException(status_code=401, detail="Bóveda bloqueada.")
    return {
        "status": "success",
        "config": {
            "model_name": vault_instance.get_secret("DEFAULT_MODEL", "gemini/gemini-1.5-flash"),
            "has_gemini_key": bool(vault_instance.get_secret("GEMINI_API_KEY")),
            "has_openai_key": bool(vault_instance.get_secret("OPENAI_API_KEY"))
        }
    }

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    global vault_instance
    if not vault_instance:
        raise HTTPException(status_code=401, detail="Bóveda bloqueada.")

    if req.gemini_key:
        vault_instance.set_secret("GEMINI_API_KEY", req.gemini_key.strip())
    if req.openai_key:
        vault_instance.set_secret("OPENAI_API_KEY", req.openai_key.strip())
    if req.model_name:
        vault_instance.set_secret("DEFAULT_MODEL", req.model_name.strip())

    return {"status": "success", "message": "Configuración actualizada encriptada en la USB."}

@app.post("/api/chat")
def chat(req: ChatRequest):
    global agent_instance
    if not agent_instance:
        raise HTTPException(status_code=401, detail="Bóveda no desbloqueada. Ejecute /api/unlock primero.")

    response = agent_instance.run(req.prompt, session_id=req.session_id)
    return {"status": "success", "response": response}

def run_web_dashboard(port: int = 8000):
    """Ejecuta el servidor web local."""
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    run_web_dashboard()
