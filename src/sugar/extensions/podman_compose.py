"""Sugar plugin for podman-compose."""

from __future__ import annotations

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs

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
doc_cni = {
    'cni': 'Use CNI networking for the containers.'
}
doc_systemd = {
    'systemd': 'Generate systemd service files for the containers.'
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

class SugarPodmanCompose(SugarBase):
    """Sugar plugin for podman-compose."""

    actions = [
        'attach',
        'build',
        'config',
        'cp',
        'create',
        'down',
        'events',
        'exec',
        'images',
        'kill',
        'logs',
        'ls',
        'pause',
        'port',
        'ps',
        'pull',
        'push',
        'restart',
        'rm',
        'run',
        'scale',
        'start',
        'stop',
        'top',
        'unpause',
        'up',
        'wait',
        'watch',
        'version',
        'generate-systemd',  # Podman-specific
        'network-create',    # CNI networking
        'network-rm',        # CNI networking
    ]

    @docparams(doc_common_service)
    def _cmd_attach(
        self,
        service: str = '',
        /,
        options: str = '',
    ) -> None:
        """Attach to a running container."""
        self._call_backend_app(
            'attach',
            [service],
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_build(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Build or rebuild services."""
        self._call_backend_app(
            'build',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_config(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Validate and view the Compose file."""
        self._call_backend_app(
            'config',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_no_services)
    def _cmd_cp(
        self,
        options: str = '',
    ) -> None:
        """Copy files/folders between a container and the local filesystem."""
        self._call_backend_app(
            'cp',
            [],
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_create(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create containers for a service."""
        self._call_backend_app(
            'create',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_down(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop and remove containers, networks, and volumes."""
        self._call_backend_app(
            'down',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_events(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Receive real time events from containers."""
        self._call_backend_app(
            'events',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_exec(
        self,
        service: str,
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Execute a command in a running container."""
        self._call_backend_app(
            'exec',
            [service],
            options.split(),
            cmd.split(),
        )

    @docparams(doc_common_services)
    def _cmd_images(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List images used by the created containers."""
        self._call_backend_app(
            'images',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_kill(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Kill containers."""
        self._call_backend_app(
            'kill',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """View output from containers."""
        self._call_backend_app(
            'logs',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        options: str = '',
    ) -> None:
        """List containers."""
        self._call_backend_app(
            'ls',
            [],
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_pause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pause services."""
        self._call_backend_app(
            'pause',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_no_services)
    def _cmd_port(
        self,
        service: str,
        options: str = '',
    ) -> None:
        """Print the public port for a port binding."""
        self._call_backend_app(
            'port',
            [service],
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List containers."""
        self._call_backend_app(
            'ps',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_pull(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pull service images."""
        self._call_backend_app(
            'pull',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_push(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Push service images."""
        self._call_backend_app(
            'push',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_restart(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Restart services."""
        self._call_backend_app(
            'restart',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_rm(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Remove stopped containers."""
        self._call_backend_app(
            'rm',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_run(
        self,
        service: str,
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Run a one-off command on a service."""
        self._call_backend_app(
            'run',
            [service],
            options.split(),
            cmd.split(),
        )

    @docparams(doc_common_service)
    def _cmd_scale(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """Set number of containers for a service."""
        self._call_backend_app(
            'scale',
            [service],
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services."""
        self._call_backend_app(
            'start',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_stop(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop services."""
        self._call_backend_app(
            'stop',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_top(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display the running processes of a container."""
        self._call_backend_app(
            'top',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_unpause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Unpause services."""
        self._call_backend_app(
            'unpause',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_up(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create and start containers."""
        self._call_backend_app(
            'up',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_wait(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Block until the first container stops."""
        self._call_backend_app(
            'wait',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_common_services)
    def _cmd_watch(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Watch for changes and update containers."""
        self._call_backend_app(
            'watch',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams(doc_options)
    def _cmd_version(
        self,
        options: str = '',
    ) -> None:
        """Show the podman-compose version information."""
        self._call_backend_app(
            'version',
            [],
            options.split(),
        )

    @docparams({**doc_common_services, **doc_systemd})
    def _cmd_generate_systemd(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Generate systemd service files for containers."""
        self._call_backend_app(
            'generate-systemd',
            self._get_services_names(services=services, all=all),
            options.split(),
        )

    @docparams({**doc_common_no_services, **doc_cni})
    def _cmd_network_create(
        self,
        options: str = '',
    ) -> None:
        """Create a CNI network."""
        self._call_backend_app(
            'network-create',
            [],
            options.split(),
        )

    @docparams({**doc_common_no_services, **doc_cni})
    def _cmd_network_rm(
        self,
        options: str = '',
    ) -> None:
        """Remove a CNI network."""
        self._call_backend_app(
            'network-rm',
            [],
            options.split(),
        ) 