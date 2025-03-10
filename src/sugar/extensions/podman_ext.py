"""Sugar plugin for podman compose."""

from __future__ import annotations

import io
import os
import sys

from pathlib import Path
from typing import Any, Union

import dotenv
import sh

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs
from sugar.utils import camel_to_snake, get_absolute_path

# Reuse the parameter documentation structure similar to compose.py
doc_profile = {
    'profile': 'Specify the profile name of the services you want to use.'
}
doc_service = {'service': 'Set the service for the container call.'}
doc_services = {
    'services': 'Set the services separated by comma for the container call.'
}
doc_all_services = {'all': 'Use all services for the command.'}
doc_options = {
    'options': (
        'Specify the options for the backend command. E.g.: `--options -d`.'
    )
}
doc_cmd = {
    'cmd': (
        'Specify the COMMAND for some podman-compose command. '
        'E.g.: --cmd python -c print(1).'
    )
}

doc_common_no_services = {
    **doc_profile,
    **doc_options,
}

doc_common_service = {
    **doc_profile,
    **doc_service,
    **doc_options,
}

doc_common_service_cmd = {
    **doc_profile,
    **doc_service,
    **doc_options,
    **doc_cmd,
}

doc_common_services = {
    **doc_profile,
    **doc_services,
    **doc_all_services,
    **doc_options,
}

doc_common_services_no_options = {
    **doc_profile,
    **doc_services,
    **doc_all_services,
}


class SugarPodmanComposeExt(SugarBase):
    """SugarPodmanCompose provides the podman compose commands."""

    def _load_backend_app(self) -> None:
        """Override to use podman instead of docker."""
        backend_cmd = self.config.get('backend', '')

        # Change to accept 'compose' as an alias for podman-compose
        # This allows the same configuration to work with
        # both Docker and Podman
        supported_backends = ['podman-ext', 'compose']

        if backend_cmd not in supported_backends:
            SugarLogs.raise_error(
                f'"{backend_cmd}" not supported by SugarPodmanCompose.'
                f' Supported backends are: {", ".join(supported_backends)}.',
                SugarError.SUGAR_COMPOSE_APP_NOT_SUPPORTED,
            )

        try:
            self.backend_app = sh.Command('podman-compose')
            # self.backend_args.append('compose')
        except sh.CommandNotFound:
            SugarLogs.raise_error(
                'The podman command was not found in the system. '
                'Please install podman first.',
                SugarError.SUGAR_COMMAND_NOT_FOUND,
            )

    def _load_backend_args(self) -> None:
        """
        Override to handle backend arguments differently for Podman.

        Podman compose doesn't support the --env-file flag directly,
        so we use environment variables instead.
        Podman also uses -f instead of --file for specifying compose files.
        """
        self._filter_service_profile()

        # Handle env file differently for Podman
        env_file = self.service_profile.get('env-file')
        if env_file:
            if not env_file.startswith('/'):
                # use .sugar file as reference for the working directory
                # for the .env file
                env_file = str(Path(self.file).parent / env_file)

            if not Path(env_file).exists():
                SugarLogs.print_warning(
                    f"""The env-file {env_file} was not found.
                    Continuing without it."""
                )

        config_path = []
        backend_path_arg = get_absolute_path(
            self.service_profile['config-path']
        )
        if isinstance(backend_path_arg, str):
            # Convert relative path to absolute using project root
            if not backend_path_arg.startswith('/'):
                backend_path_arg = str(
                    Path(self.file).parent / backend_path_arg
                )
            config_path.append(backend_path_arg)
        elif isinstance(backend_path_arg, list):
            config_path.extend(backend_path_arg)
        else:
            SugarLogs.raise_error(
                'The attribute config-path` just supports the data '
                f'types `string` or `list`, {type(backend_path_arg)} '
                'received.',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )

        # Use -f instead of --file for podman compose
        for p in config_path:
            self.backend_args.extend(['-f', p])

        # Add project-name if specified - use -p instead of
        # --project-name for podman
        if self.service_profile.get('project-name'):
            self.backend_args.extend(
                ['-p', self.service_profile['project-name']]
            )

    def _call_backend_app(
        self,
        action: str,
        services: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """
        Override _call_backend_app to handle environment variables.

        from .env file.
        instead of using the --env-file flag that's
        not supported by podman compose.
        """
        # Execute pre-run hooks
        extension = camel_to_snake(
            self.__class__.__name__.replace('Sugar', '')
        )
        self._execute_hooks('pre-run', extension, action)

        # Load env vars from env-file if specified
        env_vars = os.environ.copy()
        env_file = self.service_profile.get('env-file')
        if env_file:
            if not env_file.startswith('/'):
                # use .sugar file as reference for the working directory
                # for the .env file
                env_file = str(Path(self.file).parent / env_file)

            if Path(env_file).exists():
                try:
                    # Update env_vars with content from env_file
                    # Cast the result to Dict[str, str] to satisfy mypy
                    dotenv_values = {
                        k: str(v)
                        for k, v in dotenv.dotenv_values(env_file).items()
                        if v is not None
                    }
                    env_vars.update(dotenv_values)
                    if self.verbose:
                        SugarLogs.print_info(
                            f'Loaded environment variables from {env_file}'
                        )
                except ImportError:
                    SugarLogs.print_warning(
                        """python-dotenv package not found.
                        Env file variables will not be loaded."""
                    )
                except Exception as e:
                    SugarLogs.print_warning(
                        f'Failed to load env file {env_file}: {e!s}'
                    )

        sh_extras = {
            '_in': sys.stdin,
            '_out': _out,
            '_err': _err,
            '_no_err': True,
            '_env': env_vars,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = [
            *self.backend_args,
            *[action],
            *options_args,
            *services,
            *cmd_args,
        ]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> {self.backend_app} {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        p = self.backend_app(
            *positional_parameters,
            **sh_extras,
        )

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            SugarLogs.raise_error(
                f'Process {pid} killed.', SugarError.SH_KEYBOARD_INTERRUPT
            )

        self._execute_hooks('post-run', extension, action)

    @docparams(doc_common_service)
    def _cmd_attach(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """
        Attach to a service.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'attach',
            services=[service] if service else [],
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_build(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Build or rebuild services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'build', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_config(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Parse, resolve and render compose file in canonical format."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'config', services=services_names, options_args=options_args
        )

    @docparams(doc_common_no_services)
    def _cmd_cp(
        self,
        options: str = '',
    ) -> None:
        """Copy files/folders between a service container.

           and the local filesystem.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app('cp', services=[], options_args=options_args)

    @docparams(doc_common_services)
    def _cmd_create(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'create', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_down(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop and remove containers, networks."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'down', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_events(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Receive real time events from containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'events', services=services_names, options_args=options_args
        )

    @docparams(doc_common_service_cmd)
    def _cmd_exec(
        self,
        service: str = '',
        cmd: str = '',
        options: str = '',
    ) -> None:
        """Execute a command in a running container."""
        if not service:
            SugarLogs.raise_error(
                'The service parameter is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)
        self._call_backend_app(
            'exec',
            services=[service],
            options_args=options_args,
            cmd_args=cmd_args,
        )

    @docparams(doc_common_services)
    def _cmd_images(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List images used by the created containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'images', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_kill(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Kill containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'kill', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """View output from containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'logs', services=services_names, options_args=options_args
        )

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        options: str = '',
    ) -> None:
        """
        List running compose projects.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app('ls', services=[], options_args=options_args)

    @docparams(doc_common_services)
    def _cmd_pause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pause services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'pause', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_port(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Print the public port for a port binding."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'port', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'ps', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_pull(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pull service images."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'pull', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_push(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Push service images."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'push', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_restart(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Restart services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'restart', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_rm(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Remove stopped containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'rm', services=services_names, options_args=options_args
        )

    @docparams(doc_common_service_cmd)
    def _cmd_run(
        self,
        service: str = '',
        cmd: str = '',
        options: str = '',
    ) -> None:
        """Run a one-off command on a service."""
        if not service:
            SugarLogs.raise_error(
                'The service parameter is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)

        self._call_backend_app(
            'run',
            services=[service],
            options_args=options_args,
            cmd_args=cmd_args,
        )

    @docparams(doc_common_services)
    def _cmd_scale(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Scale services.

        Note: This is an experimental feature.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'scale', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'start', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_stop(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'stop', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_top(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display the running processes."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'top', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_unpause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Unpause services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'unpause', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_up(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create and start containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'up', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_version(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Show the podman-compose version information."""
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'version', services=[], options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_wait(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Block until the first service container stops.

        Note: This is an experimental feature.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'wait', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_watch(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Watch build context for service source code changes and.

        rebuild/refresh containers.

        Note: This is an experimental feature.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'watch', services=services_names, options_args=options_args
        )
