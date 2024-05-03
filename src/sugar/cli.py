"""Definition of the CLI structure."""
from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Any, List, Tuple

import typer

from typer import Argument, Option

from sugar.core import Sugar, __version__

state = {
    'verbose': False,
    'options': [],
    'cmd': [],
}


def extract_options_and_cmd_args() -> Tuple[List, List]:
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


def create_app():
    """Create app function to instantiate the typer app dinamically."""
    options_args, cmd_args = extract_options_and_cmd_args()
    state['options'] = options_args
    state['cmd'] = cmd_args

    sugar_app = typer.Typer(
        name='sugar',
        help=(
            'sugar (or sugar) is a tool that help you to organize'
            "and simplify your containers' stack."
        ),
        epilog=(
            'If you have any problem, open an issue at: '
            'https://github.com/osl-incubator/sugar'
        ),
        short_help="sugar (or sugar) is a tool that help you \
          to organize containers' stack",
    )

    ext_group = typer.Typer(
        help='Specify the plugin/extension for the command list',
        invoke_without_command=True,
        options_metavar=None,
    )

    stats_group = typer.Typer(
        help='Specify the plugin/extension for the command list',
        invoke_without_command=True,
        options_metavar=None,
    )

    # -- Add typer groups --

    sugar_app.add_typer(ext_group, name='ext')
    sugar_app.add_typer(stats_group, name='stats')

    # -- Callbacks --
    def version_callback(version: bool):
        """
        Version callback function, that will \
        be called when using the --version flag
        """
        if version:
            typer.echo(f'Version: {__version__}')
            raise typer.Exit()

    @sugar_app.callback(invoke_without_command=True)
    def main(
        ctx: typer.Context,
        version: bool = Option(
            None,
            '--version',
            '-v',
            callback=version_callback,
            is_flag=True,
            is_eager=True,
            help='Show the version of sugar.',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ) -> None:
        """Process commands for specific flags; \
        otherwise, show the help menu.
        """
        ctx.ensure_object(dict)

        if verbose:
            state['verbose'] = True

        if ctx.invoked_subcommand is None:
            typer.echo('Welcome to sugar. For usage, try --help.')
            raise typer.Exit()

    # -- Main commands --

    @sugar_app.command()
    def build(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help=(
                'Set the services for the container call.'
                " Use comma to separate the services's name"
            ),
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help=(
                'Specify the options for docker-compose command. '
                'E.g.: --options -d'
            ),
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help=(
                'Specify the COMMAND for some docker-compose command. '
                'E.g.: --cmd python -c print(1)'
            ),
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'build'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def config(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help=(
                'Set the services for the container call.'
                " Use comma to separate the services's name"
            ),
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command. \
                  E.g.: --options -d',
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command. \
                  E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'config'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def create(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call. \
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command. \
                  E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command. \
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'create'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def down(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call. \
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command. \
                E.g.: --options -d',
        ),
        rmi: str = Option(
            None,
        ),
        remove_orphans: str = Option(
            None,
        ),
        volumes: str = Option(
            None,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'down'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def events(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help=(
                'Set the services for the container call.'
                " Use comma to separate the services's name"
            ),
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help=(
                'Specify the options for docker-compose command. '
                'E.g.: --options -d'
            ),
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help=(
                'Specify the COMMAND for some docker-compose command. '
                'E.g.: --cmd python -c print(1)'
            ),
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'events'

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command(name='exec')
    def exec_command(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help=(
                'Set the services for the container call.'
                " Use comma to separate the services's name"
            ),
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command. \
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'exec'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def images(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call. \
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'images'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def kill(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'kill'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def logs(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'logs'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def pause(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Argument(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Argument(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'pause'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def port(
        ctx: typer.Context,
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        private_port: str = Argument(
            None, help='Specify the service private port'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'port'

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def ps(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'ps'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def pull(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'pull'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def push(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'push'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def restart(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'restart'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def rm(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for rm command: --options [-f | -s]',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'rm'

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def run(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        target: str = Option(None, '-p', help='Specify the target option.'),
        volume: str = Option(None, '-v', help='Specify the volume option.'),
        env_vars: str = Option(
            None,
            '-e',
            '-l',
            help='Specify the environment variables. [-e KEY=VAL...]',
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'run'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def start(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'start'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def stop(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'stop'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def top(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'top'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def unpause(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Argument(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Argument(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'unpause'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def up(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        scale: str = Option(
            None,
            help='Specify the service scale as an option\
                [--scale SERVICE=NUM...]',
        ),
        no_color: str = Option(
            None, help='Specify the no-color as an option.'
        ),
        quiet_pull: str = Option(
            None, help='Specify the quiet-pull as an option.'
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'up'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def version(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'version'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    # -- Ext Comamnds

    @ext_group.command(name='get-ip')
    def get_ip(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'get-ip'

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @ext_group.command(name='start')
    def ext_start(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'start'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @ext_group.command(name='stop')
    def ext_stop(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'stop'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @ext_group.command(name='restart')
    def ext_restart(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'restart'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @ext_group.command()
    def wait(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        options: str = Option(
            None,
            help='Specify the options for docker-compose command.\
                E.g.: --options -d',
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        cmd: str = Option(
            None,
            help='Specify the COMMAND for some docker-compose command.\
                E.g.: --cmd python -c print(1)',
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'wait'

        if verbose or state['verbose']:
            args['verbose'] = True

        cmd_args: List[Any] = state['cmd']
        opts_args: List[Any] = state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    # -- Stats Commands --

    @stats_group.command()
    def plot():
        print('Plot command')

    return sugar_app


app = create_app()

if __name__ == '__main__':
    app()
