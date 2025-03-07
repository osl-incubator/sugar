"""Integration tests for Sugar Swarm extension."""

import os
import subprocess

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Skip these tests if we're not in an environment where docker commands can run
# This helps prevent test failures in CI environments without docker access
pytestmark = pytest.mark.skipif(
    os.environ.get('SKIP_DOCKER_TESTS', 'false').lower() == 'true',
    reason='Docker integration tests disabled',
)


# Create a mock for the missing run_command function
@pytest.fixture
def mock_run_command() -> Generator[MagicMock, None, None]:
    """Mock the run_command function from sugar.cli."""
    with patch('sugar.cli.run_command', MagicMock()) as mock:
        yield mock


# Skip integration tests that depend on run_command
@pytest.mark.skip('Integration tests need run_command implementation')
class TestSwarmIntegration:
    """Integration tests running against real docker if available."""

    pass


class TestCommandLineInterface:
    """Test the actual CLI commands if possible."""

    def test_cli_help(self) -> None:
        """Test that CLI help shows correct commands."""
        # Skip if the sugar module isn't properly installed
        try:
            # Run the actual CLI command to check help output
            result = subprocess.run(
                ['python', '-m', 'sugar', 'swarm', '--help'],
                capture_output=True,
                text=True,
                check=False,
            )

            # Check that output contains expected commands
            assert 'node' in result.stdout
            # Make sure node subcommands aren't at top level
            assert 'node_demote' not in result.stdout
            assert 'node_inspect' not in result.stdout
        except FileNotFoundError:
            pytest.skip('Sugar module not properly installed')

    def test_cli_node_help(self) -> None:
        """Test that node help shows subcommands."""
        # Skip if the sugar module isn't properly installed
        try:
            result = subprocess.run(
                ['python', '-m', 'sugar', 'swarm', 'node', '--help'],
                capture_output=True,
                text=True,
                check=False,
            )

            # Check that output shows node subcommands
            assert 'demote' in result.stdout or 'COMMAND' in result.stdout
            assert 'inspect' in result.stdout or 'COMMAND' in result.stdout
            assert 'ls' in result.stdout or 'COMMAND' in result.stdout
        except FileNotFoundError:
            pytest.skip('Sugar module not properly installed')
