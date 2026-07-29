import os
import yaml
from typing import Dict, Any, List
from core.agent import PortableAgent

class WorkflowEngine:
    """
    Motor de Plantillas y Automatizaciones (Agent Workflows).
    Ejecuta secuencias complejas de tareas en orden (ej: 'morning_briefing').
    """

    def __init__(self, agent: PortableAgent):
        self.agent = agent

    def execute_workflow_dict(self, workflow_data: Dict[str, Any], session_id: str = "workflow_session") -> List[Dict[str, Any]]:
        """Ejecuta un flujo de trabajo definido por un diccionario de pasos."""
        name = workflow_data.get("name", "Unnamed Workflow")
        steps = workflow_data.get("steps", [])
        results = []

        for idx, step in enumerate(steps, 1):
            prompt = step.get("prompt")
            if prompt:
                res = self.agent.run(prompt, session_id=session_id)
                results.append({
                    "step": idx,
                    "name": step.get("name", f"Step {idx}"),
                    "result": res
                })

        return results

    def execute_morning_briefing(self) -> str:
        """Flujo predefinido de Morning Briefing."""
        briefing_workflow = {
            "name": "Morning Briefing",
            "steps": [
                {"name": "Consultar Agenda", "prompt": "Consultar mi calendario y próximas reuniones de hoy"},
                {"name": "Revisar Correos", "prompt": "Buscar correos no leídos importantes"}
            ]
        }
        res_list = self.execute_workflow_dict(briefing_workflow)
        summary = "☕ **Resumen de tu Morning Briefing**:\n\n"
        for item in res_list:
            summary += f"### {item['name']}\n{item['result']}\n\n"
        return summary
