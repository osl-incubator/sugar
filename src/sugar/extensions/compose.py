"""Sugar plugin for docker compose."""

from __future__ import annotations

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarErrorType, SugarLogs

doc_group = {
    'group': 'Specify the group name of the services you want to use.'
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
        'Specify the COMMAND for some docker-compose command. '
        'E.g.: --cmd python -c print(1).'
    )
}

doc_common_no_services = {
    **doc_group,
    **doc_options,
}

doc_common_service = {
    **doc_group,
    **doc_service,
    **doc_options,
}

doc_common_services = {
    **doc_group,
    **doc_services,
    **doc_all_services,
    **doc_options,
}


class SugarCompose(SugarBase):
    """SugarCompose provides the docker compose commands."""

    @docparams(doc_common_service)
    def _cmd_attach(
        self,
        group: str = '',
        service: str = '',
        options: str = '',
    ) -> None:
        """
        Attach to a service's running container.

        Attach local standard input, output, and error streams to a service's
        running container.

        Note: This is an experimental feature.
        """
        service_name = self.args.get('service', '')
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('attach', services=service_name_list)

    @docparams(doc_common_services)
    def _cmd_build(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Build or rebuild services."""
        self._call_backend_app('build', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_config(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Parse, resolve and render compose file in canonical format."""
        self._call_backend_app('config', services=self.service_names)

    @docparams(doc_common_no_services)
    def _cmd_cp(
        self,
        group: str = '',
        options: str = '',
    ) -> None:
        """
        Copy files/folders between a services and local filesystem.

        Note: This is an experimental feature.
        """
        self._call_backend_app('cp', services=[])

    @docparams(doc_common_services)
    def _cmd_create(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create containers for a service."""
        self._call_backend_app('create', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_down(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop and remove containers, networks."""
        if self.args.get('all') or self.args.get('services'):
            SugarLogs.raise_error(
                "The `down` sub-command doesn't accept `--all` "
                'neither `--services` parameters.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )

        self._call_backend_app(
            'down',
            '--remove-orphans',
            services=[],
        )

    @docparams(doc_common_services)
    def _cmd_events(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Receive real time events from containers."""
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list = [service_name] if service_name else []
        self._call_backend_app('events', services=service_name_list)

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_exec(
        self,
        group: str = '',
        service: str = '',
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Execute a command in a running container."""
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )

        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('exec', services=service_name_list)

    @docparams(doc_common_services)
    def _cmd_images(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List images used by the created containers."""
        self._call_backend_app('images', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_kill(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Force stop service containers."""
        self._call_backend_app('kill', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_logs(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """View output from containers."""
        self._call_backend_app('logs', services=self.service_names)

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        group: str = '',
        options: str = '',
    ) -> None:
        """
        List running compose projects.

        Note: This is an experimental feature.
        """
        self._call_backend_app('ls', services=[])

    @docparams(doc_common_services)
    def _cmd_pause(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pause services."""
        self._call_backend_app('pause', services=self.service_names)

    @docparams(doc_common_no_services)
    def _cmd_port(
        self,
        group: str = '',
        options: str = '',
    ) -> None:
        """Print the public port for a port binding."""
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        # TODO: check how private port could be passed
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('port', services=service_name_list)

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List containers."""
        self._call_backend_app('ps', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_pull(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pull service images."""
        self._call_backend_app('pull', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_push(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Push service images."""
        self._call_backend_app('push', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_restart(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Restart service containers."""
        self._call_backend_app('restart', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_rm(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Remove stopped service containers.

        By default, anonymous volumes attached to containers will not be
        removed. You can override this with -v. To list all volumes, use
        "docker volume ls".

        Any data which is not in a volume will be lost.
        """
        self._call_backend_app('rm', services=self.service_names)

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_run(
        self,
        group: str = '',
        service: str = '',
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Run a one-off command on a service."""
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`run` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('run', services=service_name_list)

    @docparams(doc_common_service)
    def _cmd_scale(
        self,
        group: str = '',
        service: str = '',
        options: str = '',
    ) -> None:
        """
        Scale services.

        Note: This is an experimental feature.
        """
        self._call_backend_app('scale', services=[])

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services."""
        self._call_backend_app('start', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_stop(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop services."""
        self._call_backend_app('stop', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_top(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display the running processes."""
        self._call_backend_app('top', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_unpause(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Unpause services."""
        self._call_backend_app('unpause', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_up(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create and start containers."""
        self._call_backend_app('up', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_wait(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Block until the first service container stops.

        Note: This is an experimental feature.
        """
        self._call_backend_app('wait', services=self.service_names)

    @docparams(doc_common_services)
    def _cmd_watch(
        self,
        group: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Watch build context.

        Watch build context for service and rebuild/refresh containers when
        files are updated.

        Note: This is an experimental feature.
        """
        self._call_backend_app('watch', services=self.service_names)

    @docparams(doc_options)
    def _cmd_version(
        self,
        options: str = '',
    ) -> None:
        """Show the Docker Compose version information."""
        self._call_backend_app('version', services=[])
