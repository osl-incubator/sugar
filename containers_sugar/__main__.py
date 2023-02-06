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
        choices=['help'] + Sugar.ACTIONS,
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
        '--all',
        action='store_true',
        help='Use all services for the command.',
    )
    parser.add_argument(
        '--extras',
        type=str,
        default='',
        help='Set extra arguments to be used by the compose app.',
    )
    parser.add_argument(
        '--cmd',
        type=str,
        help='Set the command to be used by run/exec.',
    )
    parser.add_argument(
        '--config-file',
        type=str,
        default=str(Path(os.getcwd()) / '.containers-sugar.yaml'),
        help='Specify a custom location for the config file.',
    )
    return parser


def show_version():
    print('containers-sugar version:', __version__)


def app():
    args_parser = _get_args()
    args = args_parser.parse_args()

    if args.action == 'help':
        return args_parser.print_help()

    sugar = Sugar(args)

    if args.action == 'version':
        show_version()
        sugar.run()
        return

    sugar.load_services()
    return sugar.run()


if __name__ == '__main__':
    app()
