"""Tests for `sugar` package."""

from copy import deepcopy
from pathlib import Path

import pytest

from sugar.core import Sugar

CONFIG_PATH = Path(__file__).parent.parent / '.sugar.yaml'
DEFAULT_ARGS = {
    'backend-app': 'docker compose',
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


@pytest.mark.parametrize(
    'args',
    [
        {'help': True},
        {'plugin': 'compose', 'action': 'version', 'version': True},
        {'plugin': 'compose', 'help': True},
        {'plugin': 'compose', 'action': 'config', 'service_group': 'group1'},
        {'plugin': 'compose-ext', 'action': 'version', 'version': True},
        {'plugin': 'compose-ext', 'help': True},
        {
            'plugin': 'compose-ext',
            'action': 'config',
            'service_group': 'group1',
        },
    ],
)
def test_success(args):
    """Test success cases."""
    args.update(
        {
            'config_file': str(CONFIG_PATH.absolute()),
            'verbose': True,
        }
    )
    args_obj = deepcopy(DEFAULT_ARGS)
    args_obj.update(args)
    print(args_obj)

    s = Sugar(args_obj)
    s.run()
