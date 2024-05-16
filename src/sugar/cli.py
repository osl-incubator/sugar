"""Definition of the CLI structure."""

from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Any, Dict, Tuple

import typer

from typer import Argument, Option

from sugar.core import Sugar, __version__

flags_state: Dict[str, bool] = {
    'verbose': False,
}

opt_state: Dict[str, list[Any]] = {
    'options': [],
    'cmd': [],
}


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


def create_main_group(sugar_app: typer.Typer):
    """
    Create the main plugin command group.

    Also add the commands to sugar app.
    """
    # -- Main commands --

    @sugar_app.command()
    def attach(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
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
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Attach to a service's running container.

        Attach local standard input, output, and error streams to a service's
        running container.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'attach'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Build or rebuild services."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'build'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Parse, resolve and render compose file in canonical format."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'config'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def cp(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        options: str = Option(
            None,
            help=(
                'Specify the options for docker-compose command. '
                'E.g.: --options -d'
            ),
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Copy files/folders between a services and local filesystem.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'cp'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Create containers for a service."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'create'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Stop and remove containers, networks."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'down'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
    ):
        """Receive real time events from containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'events'

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        """Execute a command in a running container."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'exec'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """List images used by the created containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'images'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Force stop service containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'kill'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """View output from containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'logs'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def ls(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        List running compose projects.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'ls'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Pause services."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'pause'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def port(
        ctx: typer.Context,
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
    ):
        """Print the public port for a port binding."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'port'

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """List containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'ps'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Pull service images."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'pull'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Push service images."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'push'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Restart service containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'restart'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Remove stopped service containers.

        By default, anonymous volumes attached to containers will not be
        removed. You can override this with -v. To list all volumes, use
        "docker volume ls".

        Any data which is not in a volume will be lost.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'rm'

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        """Run a one-off command on a service."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'run'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def scale(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Scale services.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'scale'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Start services."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'start'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Stop services."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'stop'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Display the running processes."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'top'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Unpause services."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'unpause'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Create and start containers."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'up'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
    def version(
        ctx: typer.Context,
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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Show the Docker Compose version information."""
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'version'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    @sugar_app.command()
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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Block until the first service container stops.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'wait'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()

    @sugar_app.command()
    def watch(
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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """
        Watch build context.

        Watch build context for service and rebuild/refresh containers when
        files are updated.

        Note: This is an experimental feature.
        """
        args = ctx.params
        args['plugin'] = 'main'
        args['action'] = 'watch'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args).run()


def create_ext_group(sugar_app: typer.Typer):
    """
    Create a command group for ext plugin.

    The function also associate the group to sugar app.
    """
    ext_group = typer.Typer(
        help='(PLUGIN) Use the `ext` plugin.',
        invoke_without_command=True,
    )

    # -- Ext Commands

    @ext_group.command(name='get-ip')
    def get_ip(
        ctx: typer.Context,
        service_group: str = Option(
            None,
            '--service-group',
            '--group',
            help='Specify the group name of the services you want to use',
        ),
        service: str = Option(
            None, help='Set the service for the container call.'
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
    ):
        """Get the IP for given service (NOT IMPLEMENTED YET)."""
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'get-ip'

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Run `up` main command (alias)."""
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'start'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Run the main stop command (alias)."""
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'stop'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Run `down` and `up` sequentially."""
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'restart'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

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
        timeout: str = Option(
            None, help='Set the timeout for waiting for the service'
        ),
        config_file: str = Option(
            str(Path(os.getcwd()) / '.sugar.yaml'),
            help='Specify a custom location for the config file.',
            is_flag=True,
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Wait until the service are healthy (NOT IMPLEMENTED YET)."""
        args = ctx.params
        args['plugin'] = 'ext'
        args['action'] = 'wait'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    sugar_app.add_typer(ext_group, name='ext')


def create_stats_group(sugar_app: typer.Typer):
    """Instantiate the stats command group."""
    stats_group = typer.Typer(
        help='(PLUGIN) Use the `stats` plugin.',
        invoke_without_command=True,
    )

    # -- Stats Commands --

    @stats_group.command()
    def plot(
        ctx: typer.Context,
        services: str = Option(
            None,
            help="Set the services for the container call.\
                Use comma to separate the services's name",
        ),
        all: bool = Option(
            False,
            help='Use all services for the command.',
            is_flag=True,
        ),
        verbose: bool = Option(
            False,
            '--verbose',
            is_flag=True,
            is_eager=True,
            help='Show the command executed.',
        ),
    ):
        """Plot stats in real-time for given services (EXPERIMENTAL)."""
        args = ctx.params
        args['plugin'] = 'stats'
        args['action'] = 'wait'

        if verbose or flags_state['verbose']:
            args['verbose'] = True

        cmd_args: list[Any] = opt_state['cmd']
        opts_args: list[Any] = opt_state['options']

        Sugar(args, options_args=opts_args, cmd_args=cmd_args).run()

    sugar_app.add_typer(stats_group, name='stats')


def create_app():
    """Create app function to instantiate the typer app dinamically."""
    options_args, cmd_args = extract_options_and_cmd_args()
    opt_state['options'] = options_args
    opt_state['cmd'] = cmd_args

    sugar_app = typer.Typer(
        name='sugar',
        help=(
            'Sugar is a tool that help you to organize'
            "and simplify your containers' stack."
        ),
        epilog=(
            'If you have any problem, open an issue at: '
            'https://github.com/osl-incubator/sugar'
        ),
        short_help="Sugar is a tool that help you \
          to organize containers' stack",
    )

    # -- Add typer groups --

    create_main_group(sugar_app)
    create_ext_group(sugar_app)
    create_stats_group(sugar_app)

    # -- Callbacks --
    def version_callback(version: bool):
        """
        Version callback function.

        This will be called when using the --version flag
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
        """
        Process commands for specific flags.

        Otherwise, show the help menu.
        """
        ctx.ensure_object(dict)

        if verbose:
            flags_state['verbose'] = True

        if ctx.invoked_subcommand is None:
            typer.echo('Welcome to sugar. For usage, try --help.')
            raise typer.Exit()

    return sugar_app


app = create_app()

if __name__ == '__main__':
    app()
