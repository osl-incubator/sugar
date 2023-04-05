"""Tests for `containers-sugar` package."""
from dataclasses import dataclass
from pathlib import Path

import pytest

from containers_sugar import Sugar

CONFIG_PATH = Path(__file__).parent.parent / '.containers-sugar.yaml'


@dataclass
class Args:
    action: str = ''
    config_file: str = ''
    service_group: str = ''
    service: str = ''
    services: str = ''
    extras: str = ''
    all: bool = False
    version: bool = False
    verbose: bool = False
    help: bool = False


@pytest.mark.parametrize(
    'args',
    [
        {'version': True},
        {'help': True},
        {'action': 'config', 'service_group': 'group1', 'extras': ''},
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

    args_obj = Args(**args)
    print(args_obj)

    s = Sugar(args_obj)

    if not args_obj.version and not args_obj.help:
        s.load_services()
        s.run()
