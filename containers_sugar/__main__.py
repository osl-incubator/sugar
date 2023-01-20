import argparse
import os
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
        choices=['help', 'version'] + Sugar.ACTIONS,
        help='Specify the command to be performed.',
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
        '--config-file',
        type=str,
        default=str(Path(os.getcwd()) / '.containers-sugar.yaml'),
        help='Specify a custom location for the config file.',
    )
    return parser


def show_version():
    print(__version__)


def app():
    args_parser = _get_args()
    args = args_parser.parse_args()

    if args.action == 'help':
        return args_parser.print_help()

    if args.action == 'version':
        return show_version()

    sugar = Sugar(args)
    return sugar.run()


if __name__ == '__main__':
    app()
