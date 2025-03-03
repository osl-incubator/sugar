"""Tests for `sugar` package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from sugar.core import extensions
from sugar.extensions.base import SugarBase

CONFIG_PATH = Path(__file__).parent.parent / '.sugar.yaml'

SUGAR_ARGS = {
    'file': str(CONFIG_PATH.absolute()),
    'profile': 'group1',
    'verbose': True,
}

COMPOSE = extensions['compose']()
COMPOSE_EXT = extensions['compose-ext']()
STATS = extensions['stats']()

COMPOSE.load(**SUGAR_ARGS)  # type: ignore
COMPOSE_EXT.load(**SUGAR_ARGS)  # type: ignore
STATS.load(**SUGAR_ARGS)  # type: ignore


@pytest.mark.parametrize(
    'ext,action,args',
    [
        (COMPOSE, 'version', {}),
        (COMPOSE, 'config', {}),
        (COMPOSE, 'ls', {}),
        (COMPOSE, 'ps', {}),
        (COMPOSE_EXT, 'version', {}),
        (COMPOSE_EXT, 'config', {}),
        (COMPOSE_EXT, 'ls', {}),
        (COMPOSE_EXT, 'ps', {}),
    ],
)
def test_success(ext: SugarBase, action: str, args: dict[str, Any]) -> None:
    """Test success cases."""
    getattr(ext, f'_cmd_{action}')(**args)
