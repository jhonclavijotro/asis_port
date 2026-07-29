import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class MemoryManager:
    """
    Gestor de Memoria Persistente Episódica y Semántica para el Asistente Portable.
    Usa SQLite para máxima ligereza y portabilidad sin dependencias pesadas.
    """

    def __init__(self, db_filepath: str):
        self.db_filepath = os.path.abspath(db_filepath)
        os.makedirs(os.path.dirname(self.db_filepath), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_filepath)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Inicializa las tablas relacionales de la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabla 1: Historial de Conversaciones (Memoria Episódica)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla 2: Memoria de Conocimiento / Preferencias (Memoria Semántica)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key_concept TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla 3: Manual de Herramientas e Instrucciones Autoinyectadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_manual (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    usage_guide TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Memoria Episódica (Chat History) ---

    def add_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Añade un mensaje al historial de chat."""
        meta_str = json.dumps(metadata) if metadata else None
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_history (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, meta_str),
            )
            conn.commit()

    def get_chat_history(
        self, session_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Recupera los últimos N mensajes de una sesión."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content, metadata, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
            return [
                {
                    "role": row["role"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "timestamp": row["timestamp"],
                }
                for row in rows
            ]

    # --- Memoria Semántica (Preferencias y Conocimiento) ---

    def store_semantic_fact(
        self, category: str, key_concept: str, content: str, tags: Optional[List[str]] = None
    ) -> None:
        """Guarda o actualiza un hecho relevante en la memoria semántica."""
        tags_str = ",".join(tags) if tags else ""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO semantic_memory (category, key_concept, content, tags, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key_concept) DO UPDATE SET
                    category = excluded.category,
                    content = excluded.content,
                    tags = excluded.tags,
                    updated_at = excluded.updated_at
                """,
                (category, key_concept, content, tags_str, now),
            )
            conn.commit()


    def search_semantic_memory(self, query: str) -> List[Dict[str, Any]]:
        """Busca conceptos en la memoria semántica por coincidencia de palabras clave."""
        pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category, key_concept, content, tags, updated_at
                FROM semantic_memory
                WHERE key_concept LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC
                """,
                (pattern, pattern, pattern),
            )
            rows = cursor.fetchall()
            return [
                {
                    "category": r["category"],
                    "key_concept": r["key_concept"],
                    "content": r["content"],
                    "tags": r["tags"].split(",") if r["tags"] else [],
                    "updated_at": r["updated_at"],
                }
                for r in rows
            ]

    # --- Manual de Herramientas (FUTURO.md Item 1) ---

    def inject_system_manual(self, manual_entries: List[Dict[str, str]]) -> None:
        """Pobla el manual de herramientas para consulta del agente."""
        with self._get_connection() as conn:
            for entry in manual_entries:
                conn.execute(
                    """
                    INSERT INTO system_manual (tool_name, description, usage_guide)
                    VALUES (?, ?, ?)
                    ON CONFLICT(tool_name) DO UPDATE SET
                        description = excluded.description,
                        usage_guide = excluded.usage_guide
                    """,
                    (entry["tool_name"], entry["description"], entry["usage_guide"]),
                )
            conn.commit()

    def get_tool_guide(self, tool_name: str) -> Optional[Dict[str, str]]:
        """Obtiene la guía de uso de una herramienta específica."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tool_name, description, usage_guide FROM system_manual WHERE tool_name = ?",
                (tool_name,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "tool_name": row["tool_name"],
                    "description": row["description"],
                    "usage_guide": row["usage_guide"],
                }
            return None
