import time
import threading
import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from brain import app
from tools import execute_docker_command

server = FastAPI(title="SYNAPSE-X API Gate")

def monitor_loop():
    print("--- [SYNAPSE-X] PATRULLA ACTIVA ---")
    while True:
        # 1. Ejecutamos el comando de docker
        check = execute_docker_command('ps -a --filter status=exited --format {{.Names}}')
        
        # LOG CRÍTICO: ¿Qué está viendo Python realmente?
        found = check["output"].strip()
        print(f"--- [DEBUG] Escaneando Fedora... detectado: '{found}' ---")

        if found:
            # Tomamos el primer contenedor de la lista
            container = found.split('\n')[0]
            print(f"--- [SYNAPSE-X] ¡OBJETIVO DETECTADO!: {container} ---")

            # Invocamos a la IA
            state = {
                "raw_logs": f"CRITICAL: Container {container} has exited",
                "retry_count": 0,
                "execution_history": []
            }
            print("--- [SYNAPSE-X] LLAMA-3 PENSANDO... ---")
            final_state = app.invoke(state)

            # ENVIAR A N8N (Usando la IP que te funcionó con CURL)
            try:
                url_n8n = "http://172.17.0.1:5678/webhook-test/synapse-report"
                payload = {
                    "diagnosis": final_state.get("diagnosis", "Sin diagnóstico"),
                    "action": f"restart {container}",
                    "status": "success"
                }
                print(f"--- [DEBUG] Intentando enviar a n8n: {url_n8n} ---")
                res = requests.post(url_n8n, json=payload, timeout=10)
                print(f"--- [SYNAPSE-X] REPORTE ENVIADO. STATUS: {res.status_code} ---")
            except Exception as e:
                print(f"--- [ERROR DE RED] No pude llegar a n8n: {e} ---")

        # Esperamos 10 segundos para la próxima patrulla
        time.sleep(10)

# Iniciamos el hilo de monitoreo
threading.Thread(target=monitor_loop, daemon=True).start()

class LogPayload(BaseModel):
    logs: str

@server.post("/analyze")
async def analyze(payload: LogPayload):
    final_state = app.invoke({"raw_logs": payload.logs, "retry_count": 0, "execution_history": []})
    return {"diagnosis": final_state.get("diagnosis"), "actions": final_state.get("execution_history")}

if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000)
