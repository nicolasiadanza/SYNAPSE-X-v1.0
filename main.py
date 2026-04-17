from brain import app

def simulate_alert():
    # Simulamos un log de Docker fallido
    mock_logs = "CRITICAL: Container 'database_prod' exited with code 1"
    
    initial_state = {
        "raw_logs": mock_logs,
        "retry_count": 0,
        "messages": []
    }
    
    print("Iniciando SYNAPSE-X...")
    for output in app.stream(initial_state):
        print(output)

if __name__ == "__main__":
    simulate_alert()

