import subprocess

def execute_docker_command(command: str):
    """Ejecuta comandos de Docker en el sistema local Fedora."""
    try:
        # Ejemplo: command = "ps" -> ejecuta "docker ps"
        full_command = f"docker {command}"
        print(f"--- [SYNAPSE-X] EJECUTANDO: {full_command} ---")
        
        result = subprocess.run(
            full_command.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        else:
            return {"status": "error", "output": result.stderr}
            
    except Exception as e:
        return {"status": "exception", "output": str(e)}

def restart_container(container_name: str):
    """Intenta reiniciar un contenedor específico."""
    return execute_docker_command(f"restart {container_name}")
