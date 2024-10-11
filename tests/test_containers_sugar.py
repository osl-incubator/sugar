"""Tests for `sugar` package."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from sugar.core import extensions
from sugar.extensions.base import SugarBase

CONFIG_PATH = Path(__file__).parent.parent / '.sugar.yaml'
DEFAULT_ARGS = {
    'backend': 'docker compose',
    'action': '',
    'config_file': '',
    'service_group': '',
    'service': '',
    'services': None,
    'all': False,
    'version': False,
    'verbose': False,
    'help': False,
    'plugin': 'main',
}

COMPOSE = extensions['compose']()
COMPOSE_EXT = extensions['compose-ext']()
STATS = extensions['stats']()


@pytest.mark.parametrize(
    'args,ext,action',
    [
        COMPOSE,
        'version',
        {'version': True},
        COMPOSE,
        'config',
        {'service_group': 'group1'},
        COMPOSE_EXT,
        'version',
        {'version': True},
        COMPOSE_EXT,
        'config',
        {'service_group': 'group1'},
    ],
)
def test_success(ext: SugarBase, action: str, args: dict[str, Any]) -> None:
    """Test success cases."""
    args.update(
        {
            'config_file': str(CONFIG_PATH.absolute()),
            'verbose': True,
        }
    )
    args_obj = deepcopy(DEFAULT_ARGS)
    args_obj.update(args)

    getattr(ext, f'_cmd_{action}')(args_obj)
