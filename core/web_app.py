import os
import uvicorn
from fastapi import FastAPI, HTTPException
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

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Portable AI Assistant Local Dashboard",
        "instructions": "Navega a /docs para interactuar con la API gráfica."
    }

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
