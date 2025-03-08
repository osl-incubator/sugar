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

    @docparams(doc_common_service)
    def _cmd_create(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """Create a new service."""
        service_name = self._get_service_name(service)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'create',
            services=service_name,
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_inspect(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display detailed information on one or more services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'inspect',
            services=services_names,
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Fetch logs of a service or task."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
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

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List the tasks of one or more services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'ps', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_rm(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Remove one or more services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'rm', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_rollback(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Revert changes to a service's configuration."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'rollback',
            services=services_names,
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_scale(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Scale one or multiple replicated services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_service_command(
            'scale',
            services=services_names,
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_update(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Update a service."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
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
