"""Functions for inspecting and retrieving information from containers."""

from __future__ import annotations

import re
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


def get_container_stats(container_name: str) -> tuple[float, float]:
    """
    Fetch the current memory and CPU usage of a given Docker container.

    Parameters
    ----------
        container_name (str): Name of the Docker container.

    Returns
    -------
    tuple:
        The current memory usage of the container in MB and CPU usage as
        a percentage.
    """
    command = (
        f'docker stats {container_name} --no-stream --format '
        f"'{{{{.MemUsage}}}} {{{{.CPUPerc}}}}'"
    )
    result = subprocess.run(  # nosec B602, B603
        command, capture_output=True, text=True, shell=True, check=False
    )
    output = result.stdout.strip().split()
    mem_usage_str = output[0].split('/')[0].strip()
    cpu_usage_str = output[-1].strip('%')

    mem_usage = float(re.sub(r'[^\d.]', '', mem_usage_str))
    cpu_usage = float(cpu_usage_str)

    return mem_usage, cpu_usage
