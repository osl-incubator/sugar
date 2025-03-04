"""Sugar plugin for docker swarm."""

from __future__ import annotations

import io
import os
import sys

from typing import Any, Union

import sh

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs
from sugar.utils import camel_to_snake

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
    'ps': ('List tasks running on one or more nodes, '
          'defaults to current node'),
    'rm': 'Remove one or more nodes from the swarm',
    'update': 'Update a node',
}


class SugarSwarm(SugarBase):
    """SugarSwarm provides the docker swarm commands."""

    def _load_backend_app(self) -> None:
        """Override to use docker directly instead of docker compose."""
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
        command: str,
        subcommand: str,
        services: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker swarm/service commands with proper structure."""
        # Execute pre-run hooks
        extension = camel_to_snake(
            self.__class__.__name__.replace('Sugar', '')
        )
        self._execute_hooks('pre-run', extension, subcommand)

        sh_extras = {
            '_in': sys.stdin,
            '_out': _out,
            '_err': _err,
            '_no_err': True,
            '_env': os.environ,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = [
            command,
            subcommand,
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
        self._execute_hooks('post-run', extension, subcommand)

    @docparams(doc_common_no_services)
    def _cmd_init(
        self,
        options: str = '',
    ) -> None:
        """Initialize a swarm.

        This command bypasses .sugar.yaml configuration completely.
        """
        # For swarm init, bypass the Sugar configuration completely
        # and directly call docker swarm init
        options_args = self._get_list_args(options)

        sh_extras = {
            '_in': sys.stdin,
            '_out': sys.stdout,
            '_err': sys.stderr,
            '_no_err': True,
            '_env': os.environ,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = [
            'swarm',
            'init',
            *options_args,
        ]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> docker {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        p = sh.docker(
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

    @docparams(doc_common_no_services)
    def _cmd_join(
        self,
        options: str = '',
    ) -> None:
        """Join a swarm as a node and/or manager."""
        options_args = self._get_list_args(options)
        self._call_swarm_command('swarm', 'join', options_args=options_args)

    @docparams(doc_common_service)
    def _cmd_create(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """Create a new service."""
        service_name = self._get_service_name(service)
        options_args = self._get_list_args(options)
        self._call_swarm_command(
            'service',
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
        self._call_swarm_command(
            'service',
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
        self._call_swarm_command(
            'service',
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
        self._call_swarm_command('service', 'ls', options_args=options_args)

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
        self._call_swarm_command(
            'service', 'ps', services=services_names, options_args=options_args
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
        self._call_swarm_command(
            'service', 'rm', services=services_names, options_args=options_args
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
        self._call_swarm_command(
            'service',
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
        self._call_swarm_command(
            'service',
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
        self._call_swarm_command(
            'service',
            'update',
            services=services_names,
            options_args=options_args,
        )

    # Node commands
    @docparams(
        {
            'demote': 'Demote one or more nodes from manager in the swarm',
            'inspect': 'Display detailed information on one or more nodes',
            'ls': 'List nodes in the swarm',
            'promote': 'Promote one or more nodes to manager in the swarm',
            'ps': ('List tasks running on one or more nodes, '
                  'defaults to current node'),
            'rm': 'Remove one or more nodes from the swarm',
            'update': 'Update a node',
        }
    )
    def _cmd_node(
        self,
        demote: str = '',
        inspect: str = '',
        ls: bool = False,
        promote: str = '',
        ps: str = '',
        rm: str = '',
        update: str = '',
        options: str = '',
    ) -> None:
        # Check which subcommand was provided
        subcommand = None
        node_names = []

        # Map command options to subcommands
        if demote:
            subcommand = 'demote'
            node_names = demote.split(',')
        elif inspect:
            subcommand = 'inspect'
            node_names = inspect.split(',')
        elif ls:
            subcommand = 'ls'
        elif promote:
            subcommand = 'promote'
            node_names = promote.split(',')
        elif ps:
            subcommand = 'ps'
            node_names = ps.split(',')
        elif rm:
            subcommand = 'rm'
            node_names = rm.split(',')
        elif update:
            subcommand = 'update'
            node_names = update.split(',')

        if not subcommand:
            # If no subcommand is provided, show the help message
            self._print_node_help()
            return

        if subcommand == 'ls':
            # For ls command, we don't need node names
            self._call_swarm_command('node', subcommand)
            return

        # For other commands, we need node names
        if not node_names:
            SugarLogs.raise_error(
                f'Node name(s) must be provided for the '
                f'"{subcommand}" command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        options_args = self._get_list_args(options)
        self._call_swarm_command(
            'node', subcommand, services=node_names, options_args=options_args
        )

    def _print_node_help(self) -> None:
        """Print a help message for the node.

        command that matches Docker's format.
        """
        help_text = """
        Usage:  sugar swarm node COMMAND

        Manage Swarm nodes

        Commands:
          demote      Demote one or more nodes from manager in the swarm
          inspect     Display detailed information on one or more nodes
          ls          List nodes in the swarm
          promote     Promote one or more nodes to manager in the swarm
          ps          List tasks running on one or more nodes, defaults to node
          rm          Remove one or more nodes from the swarm
          update      Update a node

        Run 'sugar swarm node COMMAND --help' for more information on a command
        """
        print(help_text)
