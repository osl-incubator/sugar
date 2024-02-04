"""Functions for inspecting and retrieving information from containers."""
import subprocess  # nosec B404


def get_container_name(container_id: str) -> str:
    """Get the container name for the given container_id."""
    cmd = ['docker', 'inspect', '--format={{.Name}}', container_id]
    result = subprocess.run(  # nosec B603
        cmd, capture_output=True, text=True, check=False
    )
    if not result.stdout:
        raise Exception('No container name found for the given ID')
    # Removing the leading slash from the container name
    return result.stdout.strip().lstrip('/')
