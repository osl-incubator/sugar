"""Definition of the CLI structure."""
import argparse
import os
import sys

from pathlib import Path
from typing import Tuple

from sugar import Sugar


def _get_args():
    """Define and return the arguments used by the CLI."""
    parser = argparse.ArgumentParser(
        prog='sugar',
        description=(
            'sugar (or sugar) is a tool that help you to organize'
            "and simplify your containers' stack."
        ),
        epilog=(
            'If you have any problem, open an issue at: '
            'https://github.com/osl-incubator/sugar'
        ),
    )

    parser.add_argument(
        'plugin',
        type=str,
        nargs='?',
        default='main',
        help='Specify the plugin/extension for the command',
    )
    parser.add_argument(
        'action',
        nargs='?',
        default=None,
        help='Specify the command to be performed.',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show the command executed.',
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show the version of sugar.',
    )
    parser.add_argument(
        '--service-group',
        '--group',
        dest='service_group',
        type=str,
        help='Specify the group name of the services you want to use',
    )
    parser.add_argument(
        '--services',
        type=str,
        help=(
            'Set the services for the container call. '
            "Use comma to separate the services's name"
        ),
    )
    parser.add_argument(
        '--service',
        type=str,
        help=('Set the service for the container call.'),
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Use all services for the command.',
    )
    parser.add_argument(
        '--config-file',
        type=str,
        default=str(Path(os.getcwd()) / '.sugar.yaml'),
        help='Specify a custom location for the config file.',
    )
    parser.add_argument(
        '--options',
        type=str,
        required=False,
        help=(
            'Specify the options for docker-compose command. '
            'E.g.: --options -d'
        ),
    )
    parser.add_argument(
        '--cmd',
        type=str,
        required=False,
        help=(
            'Specify the COMMAND for some docker-compose command. '
            'E.g.: --cmd python -c "print(1)"'
        ),
    )
    return parser


def extract_options_and_cmd_args() -> Tuple[list, list]:
    """Extract arg `options` and `cmd` from the CLI calling."""
    args = list(sys.argv)
    total_args = len(args)

    if '--options' in args:
        options_sep_idx = args.index('--options')
    else:
        options_sep_idx = None

    if '--cmd' in args:
        cmd_sep_idx = args.index('--cmd')
    else:
        cmd_sep_idx = None

    if options_sep_idx is None and cmd_sep_idx is None:
        return [], []

    # check if --pre-args or --post-args are the last ones in the command line
    first_sep_idx = min(
        [(options_sep_idx or total_args), (cmd_sep_idx or total_args)]
    )
    for sugar_arg in [
        '--verbose',
        '--version',
        '--service-group',
        '--group',
        '--services',
        '--service',
        '--all',
        '--config-file',
    ]:
        if sugar_arg not in args:
            continue

        if first_sep_idx < args.index(sugar_arg):
            print(
                '[EE] The parameters --options/--cmd should be the '
                'last ones in the command line.'
            )
            os._exit(1)

    for ind in range(first_sep_idx, total_args):
        sys.argv.pop(first_sep_idx)

    options_sep_idx = options_sep_idx or total_args
    cmd_sep_idx = cmd_sep_idx or total_args

    if options_sep_idx < cmd_sep_idx:
        options_args = args[options_sep_idx + 1 : cmd_sep_idx]
        cmd_args = args[cmd_sep_idx + 1 :]
    else:
        cmd_args = args[cmd_sep_idx + 1 : options_sep_idx]
        options_args = args[options_sep_idx + 1 :]
    return options_args, cmd_args


def app():
    """Run container-sugar app."""
    options_args, cmd_args = extract_options_and_cmd_args()
    args_parser = _get_args()
    args = args_parser.parse_args()

    args_cast = dict(args._get_kwargs())

    sugar = Sugar(args_cast, options_args, cmd_args)
    return sugar.run()
