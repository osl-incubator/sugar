"""Tests for the Stats extension."""

from pathlib import Path

import pytest

from pytest import CaptureFixture
from sugar.extensions.stats import SugarStats


@pytest.fixture
def sugar_ext() -> SugarStats:
    """Return a fixture for the Sugar extension instance."""
    test_path = Path(__file__).parent
    sugar_cmd = SugarStats()
    sugar_cmd.load(
        file=str(test_path / 'containers' / '.services.sugar.yaml'),
        dry_run=True,
        verbose=True,
    )
    return sugar_cmd


def test_cmd_plot(sugar_ext: SugarStats, capsys: CaptureFixture[str]) -> None:
    """Test plot command with all argument."""
    sugar_ext._cmd_plot(services='', all=True)
    captured = capsys.readouterr()
    for term in 'docker ps'.split(' '):
        assert term in captured.out
