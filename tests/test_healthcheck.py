import unittest
from unittest.mock import patch, MagicMock
from sugar.healthcheck import *


class TestHealthCheck(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_container_name(self, mock_subprocess):
        # Mock successful response
        mock_subprocess.return_value = MagicMock(stdout="/my_container\n", returncode=0)
        container_name = get_container_name("12345")
        self.assertEqual(container_name, "my_container")

        # Mock failure response
        mock_subprocess.return_value = MagicMock(stdout="", returncode=0)
        with self.assertRaises(ValueError):
            get_container_name("12345")

    @patch("subprocess.run")
    def test_get_container_stats(self, mock_subprocess):
        # Mock successful response
        mock_subprocess.return_value = MagicMock(stdout="50MiB / 100MiB 25.5%\n", returncode=0)
        mem_usage, cpu_usage = get_container_stats("my_container")
        self.assertEqual(mem_usage, 50.0)
        self.assertEqual(cpu_usage, 25.5)

        # Mock failure response
        mock_subprocess.return_value = MagicMock(stdout="", returncode=1, stderr="Error")
        with self.assertRaises(RuntimeError):
            get_container_stats("my_container")

        # Mock invalid memory usage
        mock_subprocess.return_value = MagicMock(stdout="N/A / 100MiB 10.0%\n", returncode=0)
        mem_usage, cpu_usage = get_container_stats("my_container")
        self.assertEqual(mem_usage, 0.0)
        self.assertEqual(cpu_usage, 10.0)

    @patch("subprocess.run")
    def test_check_container_health(self, mock_subprocess):
        # Mock `docker ps` response
        mock_subprocess.side_effect = [
            MagicMock(stdout="12345 my_container Up (healthy)\n", returncode=0),  # docker ps
            MagicMock(stdout="50MiB / 100MiB 25.5%\n", returncode=0),  # docker stats
        ]
        result = check_container_health()
        self.assertEqual(result["message"], "Health check completed.")
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "my_container")
        self.assertEqual(result["data"][0]["health"], "healthy")
        self.assertEqual(result["data"][0]["memory_usage_mb"], 50.0)
        self.assertEqual(result["data"][0]["cpu_usage_percent"], 25.5)

        # Mock no running containers
        mock_subprocess.side_effect = [
            MagicMock(stdout="", returncode=0),  # docker ps
        ]
        result = check_container_health()
        self.assertEqual(result["message"], "No running containers found.")
        self.assertEqual(len(result["data"]), 0)

        # Mock malformed container data
        mock_subprocess.side_effect = [
            MagicMock(stdout="malformed_data\n", returncode=0),  # docker ps
        ]
        result = check_container_health()
        self.assertEqual(result["message"], "Health check completed.")
        self.assertEqual(len(result["data"]), 0)


if __name__ == "__main__":
    unittest.main()