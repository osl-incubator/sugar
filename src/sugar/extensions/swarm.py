"""Sugar plugin for docker swarm."""

from __future__ import annotations

import io
import sys

from typing import Any, Union

import sh

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs

doc_profile = {
    'profile': 'Specify the profile name of the services you want to use.'
}
doc_options = {
    'options': (
        'Specify the options for the backend command. '
        'E.g.: `--options --advertise-addr 192.168.1.1`.'
    )
}
doc_service = {'service': 'Set the service for the swarm command.'}
doc_services = {
    'services': 'Set the services separated by comma for the swarm command.'
}
doc_node = {'node': 'Set the node for the swarm command.'}
doc_nodes = {
    'nodes': 'Set the nodes separated by comma for the swarm command.'
}
doc_all_services = {'all': 'Use all services for the command.'}
doc_all_nodes = {'all': 'Use all nodes for the command.'}
doc_subcommand = {'subcommand': 'Subcommand to execute for the node command.'}

doc_stack = {'stack': 'Name of the stack to deploy'}

doc_compose_file = {
    'file': """Path to a Compose file
                     (overrides the one from profile)""",
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

doc_stack_rm = {
    **doc_stack,
    **doc_options,
}

doc_common_node = {
    **doc_profile,
    **doc_node,
    **doc_options,
}

doc_common_nodes = {
    **doc_profile,
    **doc_nodes,
    **doc_all_nodes,
    **doc_options,
}

doc_node_command = {
    **doc_profile,
    **doc_options,
    **doc_nodes,
    **doc_all_nodes,
    **doc_subcommand,
}

# Node command specific docs
doc_node_options = {
    'demote': 'Demote one or more nodes from manager in the swarm',
    'inspect': 'Display detailed information on one or more nodes',
    'ls': 'List nodes in the swarm',
    'promote': 'Promote one or more nodes to manager in the swarm',
    'ps': (
        'List tasks running on one or more nodes, defaults to current node'
    ),
    'rm': 'Remove one or more nodes from the swarm',
    'update': 'Update a node',
}

doc_logs_options = {
    'details': 'Show extra details provided to logs',
    'follow': 'Follow log output',
    'no_resolve': 'Do not map IDs to Names in output',
    'no_task_ids': 'Do not include task IDs in output',
    'no_trunc': 'Do not truncate output',
    'raw': 'Do not neatly format logs',
    'since': """Show logs since timestamp
    (e.g. 2013-01-02T13:23:37Z) or relative (e.g. 42m for 42 minutes)""",
    'tail': 'Number of lines to show from the end of the logs (default all)',
    'timestamps': 'Show timestamps',
}

doc_rollback_options = {
    'detach': """Exit immediately instead
    of waiting for the service to converge""",
    'quiet': 'Suppress progress output',
}

doc_scale_options = {
    'detach': """Exit immediately instead
    of waiting for the service to converge""",
    'replicas': """Number of replicas per service
    (comma-separated list of service=replicas pairs)""",
}

doc_update_options = {
    'detach': """Exit immediately instead of waiting
    for the service to converge""",
    'quiet': 'Suppress progress output',
    'image': 'Service image tag',
    'replicas': 'Number of tasks',
    'force': 'Force update even if no changes require it',
    'rollback': 'Rollback to previous specification',
    'env_add': """Add or update environment variables
    (comma-separated list of NAME=VALUE)""",
    'label_add': """Add or update service labels
      (comma-separated list of key=value)""",
}


class SugarSwarm(SugarBase):
    """SugarSwarm provides the docker swarm commands."""

    # Override the prefix for commands that should be hidden from CLI
    # The CLI framework only looks for methods starting with _cmd_
    # By renaming these methods to start with _subcmd_ instead,
    # they won't be automatically exposed in the CLI

    def _load_backend_app(self) -> None:
        self.backend_app = sh.docker
        # Don't add a compose subcommand
        self.backend_args = []

    def _load_backend_args(self) -> None:
        """Override to prevent adding compose-specific arguments."""
        # For swarm commands, we don't need any of the
        # compose-specific arguments
        # like --env-file, --file, or --project-name
        # Deliberately override the parent's method \
        # with an empty implementation
        self.backend_args = []

    def _get_services_names(self, **kwargs: Any) -> list[str]:
        """Override to handle swarm service names without requiring config.

        For swarm commands, services are specified directly on the command line
        and don't need to be defined in a config file.
        """
        if 'all' not in kwargs and 'services' not in kwargs:
            # The command doesn't specify services
            return []

        _arg_services = kwargs.get('services', '')

        # For swarm, we don't use the 'all' flag, only explicit services
        if not _arg_services:
            SugarLogs.raise_error(
                'Service name must be provided for this command '
                '(use --services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        # Simply split the comma-separated service names
        services_list: list[str] = _arg_services.split(',')
        return services_list

    def _get_nodes_names(self, **kwargs: Any) -> list[str]:
        """Handle node names for swarm node commands.

        For swarm node commands, nodes are specified directly
          on the command line.
        """
        if 'all' not in kwargs and 'nodes' not in kwargs:
            # The command doesn't specify nodes
            return []

        _arg_nodes = kwargs.get('nodes', '')

        # For swarm, we only use explicit nodes
        if not _arg_nodes:
            SugarLogs.raise_error(
                'Node name must be provided for this command '
                '(use --nodes node1,node2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        # Simply split the comma-separated node names
        nodes_list: list[str] = _arg_nodes.split(',')
        return nodes_list

    def _call_swarm_command(
        self,
        subcommand: str,
        services: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker swarm commands with proper structure."""
        self.backend_args = ['swarm']
        self._call_backend_app(
            subcommand,
            services=services,
            options_args=options_args,
            cmd_args=cmd_args,
            _out=_out,
            _err=_err,
        )

    def _call_service_command(
        self,
        subcommand: str,
        services: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker service commands with proper structure."""
        self.backend_args = ['service']
        self._call_backend_app(
            subcommand,
            services=services,
            options_args=options_args,
            cmd_args=cmd_args,
            _out=_out,
            _err=_err,
        )

    def _call_node_command(
        self,
        subcommand: str,
        nodes: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker node commands with proper structure."""
        self.backend_args = ['node']
        self._call_backend_app(
            subcommand,
            services=nodes,  # Reusing services parameter for nodes
            options_args=options_args,
            cmd_args=cmd_args,
            _out=_out,
            _err=_err,
        )

    def _call_stack_command(
        self,
        stack_name: str,
        compose_file: str = '',
        options_args: list[str] = [],
        backend_args: list[str] = [],
        compose_file_required: bool = False,
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker stack commands with proper structure."""
        # Build the full command: stack deploy -c file stackname

        # Check if compose file should be included
        self.backend_args = backend_args.copy()
        if compose_file and compose_file_required:
            self.backend_args.extend([compose_file])

        # Call with the stack name as the main command/argument
        self._call_backend_app(
            stack_name,
            options_args=options_args,
            _out=_out,
            _err=_err,
        )

    @docparams(doc_common_no_services)
    def _cmd_init(
        self,
        options: str = '',
    ) -> None:
        """Initialize a swarm.

        This command initializes a new swarm on the current Docker engine.
        """
        # For swarm init, use the wrapper method instead
        options_args = self._get_list_args(options)
        self._call_swarm_command('init', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_join(
        self,
        options: str = '',
    ) -> None:
        """Join a swarm as a node and/or manager."""
        options_args = self._get_list_args(options)
        self._call_swarm_command('join', options_args=options_args)

    @docparams(
        {
            **doc_profile,
            **doc_stack,
            **doc_compose_file,
            **doc_options,
        }
    )
    def _cmd_create(
        self,
        /,
        stack: str = '',
        file: str = '',
        profile: str = '',
        options: str = '',
    ) -> None:
        """Deploy a new stack from a compose file.

        This command deploys a stack using the compose file specified
        either directly or from the profile configuration.
        """
        # Validate stack name
        if not stack:
            SugarLogs.raise_error(
                'Stack name must be provided for stack deployment',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        compose_file = file
        # If no file is provided, get it from the profile configuration
        if not compose_file:
            # Make sure configuration is loaded
            if not hasattr(self, 'config') or not self.config:
                # Use the load method from the parent class,
                # which is the correct method
                super().load(
                    self.file,
                    self.profile_selected,
                    self.dry_run,
                    self.verbose,
                )

            # Get the profile configuration
            profile_name = profile or self.profile_selected
            if profile_name and 'profiles' in self.config:
                profile_config = self.config['profiles'].get(profile_name, {})
                config_path = profile_config.get('config-path', '')

                # config_path can be a string or a list
                if isinstance(config_path, list) and config_path:
                    compose_file = config_path[
                        0
                    ]  # Use the first file if multiple
                else:
                    compose_file = config_path

        if not compose_file:
            SugarLogs.raise_error(
                """Compose file not specified and
                not found in profile configuration""",
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        # Parse options
        options_args = self._get_list_args(options)

        # Use the helper method instead of direct call
        self._call_stack_command(
            stack_name=stack,
            compose_file=compose_file,
            options_args=options_args,
            compose_file_required=True,
            backend_args=['stack', 'deploy', '-c'],
        )

    @docparams(
        {
            **doc_common_services,
            'format': 'Format output using a custom template',
            'size': 'Display total file sizes if the type is container',
            'type': 'Return JSON for specified type',
        }
    )  # TODO: Need to add support for service names
    def _cmd_inspect(
        self,
        services: str = '',
        all: bool = False,
        format: str = '',
        size: bool = False,
        type: str = '',
        options: str = '',
    ) -> None:
        """
        Display detailed information on Docker objects.

        Returns low-level information on Docker objects
        (containers, images, volumes,
        networks, nodes, services, tasks, etc).
        """
        services_names = self._get_services_names(services=services, all=all)

        # Prepare the options with the format flag if provided
        options_list = self._get_list_args(options)
        # TODO: Need to fix and Validate format and type values
        if format:
            options_list.extend(['--format=', format])

        if size:
            options_list.append('--size')

        if type:
            options_list.extend(['--type', type])

        # Use direct docker inspect command instead
        # of service-specific inspect

        self.backend_args = []  # Reset backend args use direct docker command
        self._call_backend_app(
            'inspect',
            services=services_names,
            options_args=options_list,
        )

    @docparams({**doc_common_services, **doc_logs_options})
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        details: bool = False,
        follow: bool = False,
        no_resolve: bool = False,
        no_task_ids: bool = False,
        no_trunc: bool = False,
        raw: bool = False,
        since: str = '',
        tail: str = '',
        timestamps: bool = False,
        options: str = '',
    ) -> None:
        """
        Fetch logs of a service or task.

        Display the logs of the specified service or task with
        advanced filtering and formatting options.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)

        # TODO: Validate since and tail values
        # Add flag options
        if details:
            options_args.append('--details')
        if follow:
            options_args.append('--follow')
        if no_resolve:
            options_args.append('--no-resolve')
        if no_task_ids:
            options_args.append('--no-task-ids')
        if no_trunc:
            options_args.append('--no-trunc')
        if raw:
            options_args.append('--raw')
        if timestamps:
            options_args.append('--timestamps')

        # Add options with values
        if since:
            options_args.extend(['--since', since])
        if tail:
            options_args.extend(['--tail', tail])

        self._call_service_command(
            'logs',
            services=services_names,
            options_args=options_args,
        )

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        options: str = '',
    ) -> None:
        """List services."""
        options_args = self._get_list_args(options)
        self._call_service_command('ls', options_args=options_args)

    @docparams(
        {
            **doc_stack_rm,
            'quiet': 'Only display IDs',
        }
    )
    def _cmd_ps(
        self,
        /,
        stack: str = '',
        quiet: bool = False,
        options: str = '',
    ) -> None:
        """List the tasks in the stack."""
        if not stack:
            SugarLogs.raise_error(
                'Stack name must be provided for stack ps command',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        backend_args = ['stack', 'ps']
        if quiet:
            backend_args = ['stack', 'ps', '--quiet']

        options_args = self._get_list_args(options)
        self._call_stack_command(
            stack_name=stack,
            options_args=options_args,
            compose_file_required=False,
            backend_args=backend_args,
        )

    @docparams(doc_stack_rm)
    def _cmd_rm(
        self,
        /,
        stack: str = '',
        options: str = '',
    ) -> None:
        """Remove the stack from the swarm."""
        self._call_stack_command(
            stack_name=stack,
            options_args=self._get_list_args(options),
            compose_file_required=False,
            backend_args=['stack', 'rm'],
        )

    @docparams({**doc_common_services, **doc_rollback_options})
    def _cmd_rollback(
        self,
        services: str = '',
        all: bool = False,
        detach: bool = False,
        quiet: bool = False,
        options: str = '',
    ) -> None:
        """
        Revert changes to a service's configuration.

        This command rolls back a service to its previous version.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)

        # Add flag options
        if detach:
            options_args.append('--detach')
        if quiet:
            options_args.append('--quiet')

        self._call_service_command(
            'rollback',
            services=services_names,
            options_args=options_args,
        )

    @docparams({**doc_common_services, **doc_scale_options})
    def _cmd_scale(
        self,
        services: str = '',
        all: bool = False,
        detach: bool = False,
        replicas: str = '',
        options: str = '',
    ) -> None:
        """
        Scale one or multiple replicated services.

        This command sets the desired number of
        replicas for each specified service.

        Format for replicas parameter: 'service1=3,service2=5'

        Scale multiple services :

        sugar swarm scale --services frontend,backend --replicas frontend=5
        ,backend=3

        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)

        # Add detach flag if specified
        if detach:
            options_args.append('--detach')

        # If replicas are specified,
        # we need to override the services_names list
        # with SERVICE=REPLICAS format that Docker expects
        if replicas:
            service_replicas_pairs = []
            replicas_dict = {}

            # Parse the replicas parameter (service=replicas,service=replicas)
            for pair in replicas.split(','):
                if '=' in pair:
                    service, count = pair.split('=', 1)
                    replicas_dict[service.strip()] = count.strip()

            # Create the properly formatted SERVICE=REPLICAS arguments
            for service in services_names:
                if service in replicas_dict:
                    service_replicas_pairs.append(
                        f'{service}={replicas_dict[service]}'
                    )
                else:
                    SugarLogs.print_warning(
                        f'No replica count specified for service: {service}'
                    )

            # Replace services_names with the SERVICE=REPLICAS format
            services_names = service_replicas_pairs
        elif services_names:
            # If no replicas specified but services are, warn the user
            SugarLogs.print_warning(
                """No replica counts specified.
                Use --replicas service1=3,service2=5"""
            )

        print(services_names)
        print(options_args)

        self._call_service_command(
            'scale',
            services=services_names,
            options_args=options_args,
        )

    @docparams({**doc_common_services, **doc_update_options})
    def _cmd_update(
        self,
        services: str = '',
        all: bool = False,
        detach: bool = False,
        quiet: bool = False,
        image: str = '',
        replicas: str = '',
        force: bool = False,
        rollback: bool = False,
        env_add: str = '',
        label_add: str = '',
        options: str = '',
    ) -> None:
        """
        Update a service.

        This command updates the configuration of one or more services.

        Examples
        --------
            # Update service image
            sugar swarm update --services my-web --image nginx:latest

            # Scale a service (update replicas)
            sugar swarm update --services api --replicas 3

            # Add environment variables
            sugar swarm update --services app --env_add
            "DEBUG=1,LOG_LEVEL=info"

            # Update with force flag and detach
            sugar swarm update --services backend --force --detach
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)

        # Add flag options
        if detach:
            options_args.append('--detach')
        if quiet:
            options_args.append('--quiet')
        if force:
            options_args.append('--force')
        if rollback:
            options_args.append('--rollback')

        # Add options with values
        if image:
            options_args.extend(['--image', image])
        if replicas:
            options_args.extend(['--replicas', replicas])

        # Process comma-separated key-value pairs
        if env_add:
            for env_pair in env_add.split(','):
                if env_pair.strip():
                    options_args.extend(['--env-add', env_pair.strip()])

        if label_add:
            for label_pair in label_add.split(','):
                if label_pair.strip():
                    options_args.extend(['--label-add', label_pair.strip()])

        self._call_service_command(
            'update',
            services=services_names,
            options_args=options_args,
        )

    # Node commands
    @docparams(doc_node_options)
    def _cmd_node(
        self,
        /,
        demote: str = '',
        inspect: str = '',
        ls: bool = False,
        promote: str = '',
        ps: str = '',
        rm: str = '',
        update: str = '',
        options: str = '',
    ) -> None:
        """
        Manage Docker Swarm nodes.

        This command provides access to node-related subcommands for

        managing Docker Swarm nodes.
        """
        if demote:
            self._subcmd_node_demote(nodes=demote, options=options)
        elif inspect:
            self._subcmd_node_inspect(nodes=inspect, options=options)
        elif ls:
            self._subcmd_node_ls(options=options)
        elif promote:
            self._subcmd_node_promote(nodes=promote, options=options)
        elif ps:
            self._subcmd_node_ps(nodes=ps, options=options)
        elif rm:
            self._subcmd_node_rm(nodes=rm, options=options)
        elif update:
            self._subcmd_node_update(nodes=update, options=options)
        else:
            SugarLogs.print_warning(
                'No node subcommand specified. '
                """Please use one of: demote, inspect, ls,
                  promote, ps, rm, update"""
            )

    @docparams(doc_common_nodes)
    def _subcmd_node_demote(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Demote one or more nodes from manager in the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "demote" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'demote', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _subcmd_node_inspect(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Display detailed information on one or more nodes."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "inspect" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'inspect', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_no_services)
    def _subcmd_node_ls(
        self,
        options: str = '',
    ) -> None:
        """List nodes in the swarm."""
        options_args = self._get_list_args(options)
        self._call_node_command('ls', options_args=options_args)

    @docparams(doc_common_nodes)
    def _subcmd_node_promote(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Promote one or more nodes to manager in the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "promote" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'promote', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _subcmd_node_ps(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """List tasks running on one or more nodes."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "ps" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'ps', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _subcmd_node_rm(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Remove one or more nodes from the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "rm" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'rm', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _subcmd_node_update(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Update a node."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                'Node name(s) must be provided for the "update" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_node_command(
            'update', nodes=node_names, options_args=options_args
        )

    def _print_node_warning(self) -> None:
        """Display warning for node commands using the CLI's own help system.

        --help lists up all subcommands.
        """
        help_text = """
        Usage: sugar swarm node [OPTIONS] COMMAND [ARGS]...
        """
        SugarLogs.print_warning(help_text)
