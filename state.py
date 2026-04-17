from typing import Annotated, TypedDict, List, Dict
from langgraph.graph.message import add_messages

class SynapseState(TypedDict):
    # Mensajes de la conversación (memoria)
    messages: Annotated[list, add_messages]
    # Logs crudos del sistema que dispararon la alerta
    raw_logs: str
    # Diagnóstico técnico de la IA
    diagnosis: str
    # Lista de comandos a ejecutar
    plan: List[str]
    # Resultados de la ejecución de comandos
    execution_history: List[Dict[str, str]]
    # Contador de intentos para evitar bucles infinitos
    retry_count: int
