"""Tests for the ComposeExt extension."""

from pathlib import Path

import pytest

from pytest import CaptureFixture
from sugar.extensions.compose_ext import SugarComposeExt


@pytest.fixture  # type: ignore[misc]
def sugar_ext() -> SugarComposeExt:
    """Return a fixture for the Sugar extension instance."""
    test_path = Path(__file__).parent
    sugar_cmd = SugarComposeExt()
    sugar_cmd.load(
        file=str(test_path / 'containers' / '.services.sugar.yaml'),
        dry_run=True,
        verbose=True,
    )
    return sugar_cmd


def test_cmd_start_all(
    sugar_ext: SugarComposeExt, capsys: CaptureFixture[str]
) -> None:
    """Test start command with all argument."""
    sugar_ext._cmd_restart(services='', all=True, options='-d')
    captured = capsys.readouterr()
    for term in 'docker compose up service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_restart_all(
    sugar_ext: SugarComposeExt, capsys: CaptureFixture[str]
) -> None:
    """Test restart command with all argument."""
    sugar_ext._cmd_restart(services='', all=True, options='-d')
    captured = capsys.readouterr()
    for term in 'docker compose stop service1-1 service1-2'.split(' '):
        assert term in captured.out

    for term in 'docker compose up service1-1 service1-2'.split(' '):
        assert term in captured.out
