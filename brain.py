import json
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from state import SynapseState
from tools import restart_container, execute_docker_command

# Configuración del modelo
llm = ChatOllama(model="llama3", temperature=0)

def perception_node(state: SynapseState):
    print("\n--- [SYNAPSE-X] PERCIBIENDO SEÑALES ---")
    logs = state.get("raw_logs", "")
    
    prompt = f"""
    Eres SYNAPSE-X, un ingeniero de sistemas autónomo.
    Analiza este log: {logs}
    
    Responde ÚNICAMENTE en este formato JSON:
    {{
        "diagnostico": "tu explicacion corta",
        "accion": "restart" o "check",
        "target": "nombre del contenedor"
    }}
    """
    response = llm.invoke(prompt)
    
    try:
        # Extraemos el contenido del mensaje y limpiamos espacios si los hay
        content = response.content.strip()
        data = json.loads(content)
    except:
        # Fallback por si la IA devuelve texto plano
        data = {"diagnostico": response.content, "accion": "check", "target": "unknown"}

    return {
        "diagnosis": data.get("diagnostico", "Sin diagnóstico"),
        "plan": [f"{data.get('accion', 'check')} {data.get('target', 'unknown')}"],
        "messages": [response]
    }

def executor_node(state: SynapseState):
    print("\n--- [SYNAPSE-X] BRAZO MECÁNICO ACTIVO ---")
    plan = state.get("plan", [])
    history = state.get("execution_history", [])

    if plan:
        action_item = plan[0]
        # Protección para el desempaquetado (unpacking)
        parts = action_item.split(" ")
        
        if len(parts) >= 2:
            action = parts[0]
            target = parts[1]
            
            if action == "restart":
                result = restart_container(target)
            else:
                result = execute_docker_command(f"inspect {target}")

            history.append({"action": action_item, "result": result["status"]})
            print(f"--- [SYNAPSE-X] RESULTADO: {result['status']} ---")
        else:
            print(f"--- [SYNAPSE-X] Acción inválida recibida: {action_item} ---")
            history.append({"action": action_item, "result": "invalid_format"})

    return {"execution_history": history}

def router_node(state: SynapseState):
    # Si ya hay algo en el historial de ejecución, terminamos para evitar bucles
    if state.get("execution_history"):
        return END
    return "executor"

# Construcción del grafo
workflow = StateGraph(SynapseState)
workflow.add_node("perception", perception_node)
workflow.add_node("executor", executor_node)

workflow.set_entry_point("perception")

# Estas son las líneas que daban error, fijate que cierren bien los paréntesis y llaves
workflow.add_conditional_edges("perception", router_node, {
    "executor": "executor",
    END: END
})

workflow.add_edge("executor", END)

app = workflow.compile()
