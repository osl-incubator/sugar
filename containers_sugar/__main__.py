import argparse
import os
import sys
from pathlib import Path

from containers_sugar import Sugar, __version__


def _get_args():
    parser = argparse.ArgumentParser(
        prog='Containers-Sugar',
        description=(
            'Containers-Sugar is a tool that help you to organize'
            "and simplify your containers' stack"
        ),
        epilog=(
            'If you have any problem, open an issue at: '
            'https://github.com/osl-incubator/containers-sugar'
        ),
    )

    parser.add_argument(
        'action',
        choices=Sugar.ACTIONS,
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
        help='Show the version of containers-sugar.',
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
        default=str(Path(os.getcwd()) / '.containers-sugar.yaml'),
        help='Specify a custom location for the config file.',
    )
    return parser


def extract_post_args() -> list:
    container_args = list(sys.argv)

    if '--' in container_args:
        sep_idx = container_args.index('--')
    else:
        sep_idx = None

    total_args = len(container_args)

    if not sep_idx:
        return []

    for ind in range(sep_idx, total_args):
        sys.argv.pop(sep_idx)
        print(sys.argv)

    return container_args[sep_idx + 1 :]


def show_version():
    print('containers-sugar version:', __version__)


def app():
    post_args = extract_post_args()
    args_parser = _get_args()
    args = args_parser.parse_args()

    sugar = Sugar(args, post_args)

    if args.version:
        show_version()
        sugar._version()
        return

    sugar.load_services()
    return sugar.run()


if __name__ == '__main__':
    app()
