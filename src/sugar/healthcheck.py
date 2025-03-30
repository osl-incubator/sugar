import subprocess
import re
import logging

logging.basicConfig(level=logging.INFO)

def get_container_name(container_id: str) -> str:
    """Get the container name for the given container_id."""
    cmd = ['docker', 'inspect', '--format={{.Name}}', container_id]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if not result.stdout:
        raise ValueError(f"No container name found for ID: {container_id}")
    
    return result.stdout.strip().lstrip('/')


def get_container_stats(container_name: str) -> tuple[float, float]:
    """Fetch memory and CPU usage of a given Docker container."""
    command = [
        "docker", "stats", container_name, "--no-stream", "--format",
        "{{.MemUsage}} {{.CPUPerc}}"
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch stats for container {container_name}: {result.stderr.strip()}")

    if not result.stdout:
        return 0.0, 0.0  # If no data is returned, assume 0 usage

    output = result.stdout.strip().split()
    mem_usage_str = output[0].split('/')[0].strip()
    cpu_usage_str = output[-1].strip('%')

    try:
        mem_usage = float(re.sub(r'[^\d.]', '', mem_usage_str))
    except ValueError:
        mem_usage = 0.0  # Default to 0.0 if parsing fails

    cpu_usage = float(cpu_usage_str)

    return mem_usage, cpu_usage


def check_container_health() -> dict:
    """Check the health status of running Docker containers and return structured data."""
    try:
        logging.info("Starting health check for Docker containers.")
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.ID}} {{.Names}} {{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout:
            return {"message": "No running containers found.", "data": []}

        containers = result.stdout.strip().split("\n")
        container_health_data = []

        for container in containers:
            container_info = container.split(" ", 2)
            if len(container_info) < 3:
                continue  # Skip malformed lines

            container_id, name, status = container_info[0], container_info[1], container_info[2]
            
            mem_usage, cpu_usage = get_container_stats(name)
            health_status = "healthy" if "(healthy)" in status.lower() else "unhealthy"

            container_health_data.append({
                "id": container_id,
                "name": name,
                "status": status,
                "health": health_status,
                "memory_usage_mb": mem_usage,
                "cpu_usage_percent": cpu_usage
            })

        return {
            "message": "Health check completed.",
            "data": container_health_data
        }

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing docker command: {e.stderr.strip()}")
        return {"error": f"Error executing docker command: {e.stderr.strip()}"}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}