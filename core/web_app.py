import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from core.vault import VaultManager
from core.memory import MemoryManager
from core.agent import PortableAgent

app = FastAPI(title="Portable AI Assistant - Local Dashboard", version="1.0.0")

# Instancia global del agente cargado
agent_instance: Optional[PortableAgent] = None

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "web_session"

class VaultInitRequest(BaseModel):
    master_passphrase: str

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
        .container { width: 900px; height: 90vh; background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
        .header { padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: rgba(17,24,39,0.8); backdrop-filter: blur(10px); }
        .header h1 { font-size: 1.25rem; font-weight: 700; color: var(--accent-color); }
        .status-badge { font-size: 0.8rem; padding: 4px 12px; background: rgba(6,182,212,0.1); border: 1px solid var(--accent-color); border-radius: 20px; color: var(--accent-color); }
        .unlock-panel { padding: 40px; text-align: center; margin: auto; max-width: 400px; }
        .unlock-panel input { width: 100%; padding: 12px; margin: 16px 0; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; font-size: 1rem; outline: none; }
        .btn { width: 100%; padding: 12px; background: var(--accent-color); border: none; border-radius: 8px; color: #000; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn:hover { opacity: 0.9; }
        .chat-panel { display: none; flex-direction: column; height: 100%; }
        .messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { padding: 14px 18px; border-radius: 12px; max-width: 80%; line-height: 1.5; font-size: 0.95rem; }
        .message.user { align-self: flex-end; background: var(--user-msg-bg); border: 1px solid #334155; }
        .message.bot { align-self: flex-start; background: var(--bot-msg-bg); border: 1px solid var(--border-color); border-left: 4px solid var(--accent-color); }
        .input-area { padding: 16px; border-top: 1px solid var(--border-color); display: flex; gap: 12px; background: var(--card-bg); }
        .input-area input { flex: 1; padding: 14px; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; outline: none; font-size: 0.95rem; }
        .input-area input:focus { border-color: var(--accent-color); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Portable AI Assistant</h1>
            <span class="status-badge" id="status-text">Bóveda Bloqueada</span>
        </div>

        <!-- Pantalla de Desbloqueo -->
        <div class="unlock-panel" id="unlock-panel">
            <h2>🔐 Desbloquear Bóveda USB</h2>
            <p style="color: #9ca3af; font-size: 0.85rem; margin-top: 8px;">Ingrese su contraseña maestra para inicializar las herramientas agénticas.</p>
            <input type="password" id="master-pass" placeholder="Contraseña Maestra">
            <button class="btn" onclick="unlockVault()">Desbloquear Bóveda</button>
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
                document.getElementById('status-text').innerText = 'Bóveda Desbloqueada (AES-256)';
            } catch (err) {
                errEl.innerText = err.message;
                errEl.style.display = 'block';
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
    global agent_instance
    try:
        storage_dir = os.path.abspath("storage")
        vault_path = os.path.join(storage_dir, "vault.enc")
        db_path = os.path.join(storage_dir, "memory.db")

        vault = VaultManager(vault_path, req.master_passphrase)
        memory = MemoryManager(db_path)
        agent_instance = PortableAgent(vault, memory)
        return {"status": "success", "message": "Bóveda USB desbloqueada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
