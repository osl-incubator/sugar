"""SugarBase classes for containers."""

from __future__ import annotations

import io
import os
import sys

from copy import deepcopy
from pathlib import Path
from typing import Any, Union

import dotenv
import sh
import yaml  # type: ignore

from jinja2 import Environment

from sugar import __version__
from sugar.logs import SugarErrorType, SugarLogs

TEMPLATE = Environment(
    autoescape=False,
    variable_start_string='${{',
    variable_end_string='}}',
)


class SugarBase:
    """SugarBase defined the base structure for the Sugar classes."""

    actions: list[str] = []
    args: dict[str, str] = {}
    config_file: str = ''
    config: dict[str, Any] = {}
    # note: it starts with a simple command
    #       it is replaced later in the execution
    backend_app: sh.Command = sh.echo
    backend_args: list[str] = []
    defaults: dict[str, Any] = {}
    env: dict[str, str] = {}
    options_args: list[str] = []
    cmd_args: list[str] = []
    service_group: dict[str, Any] = {}
    service_names: list[str] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize the actions list for all the created commands."""
        super().__init_subclass__(**kwargs)
        # Ensure each subclass has its own actions list
        cls.actions = cls.actions.copy()
        prefix = '_cmd_'
        prefix_len = len(prefix)
        for name, value in cls.__dict__.items():
            if callable(value) and name.startswith(prefix):
                action_name = name[prefix_len:]
                cls.actions.append(action_name)

    def __init__(
        self,
        args: dict[str, str],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
    ) -> None:
        """Initialize SugarBase instance."""
        self.args = deepcopy(args)
        self.options_args = deepcopy(options_args)
        self.cmd_args = deepcopy(cmd_args)
        self.config_file = self.args.get('config_file', '')
        self.config: dict[str, Any] = {}
        self.backend_args: list[str] = []
        self.defaults: dict[str, Any] = {}
        self.env: dict[str, str] = {}
        self.service_group: dict[str, Any] = {}
        self.service_names: list[str] = []

        self._load_config()
        self._load_env()
        self._load_defaults()
        self._load_root_services()
        self._verify_args()
        self._load_backend_app()
        self._load_backend_args()
        self._verify_config()
        self._load_service_names()

    def _call_backend_app_core(
        self,
        *args: str,
        services: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        sh_extras = {
            '_in': sys.stdin,
            '_out': _out,
            '_err': _err,
            '_no_err': True,
            '_env': os.environ,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = (
            self.backend_args
            + list(args)
            + (options_args or self.options_args)
            + services
            + (cmd_args or self.cmd_args)
        )

        if self.args.get('verbose'):
            print('>>>', self.backend_app, *positional_parameters)
            print('-' * 80)

        p = self.backend_app(
            *positional_parameters,
            **sh_extras,
        )

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarErrorType.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            SugarLogs.raise_error(
                f'Process {pid} killed.', SugarErrorType.SH_KEYBOARD_INTERRUPT
            )

    def _call_backend_app(
        self,
        *args: str,
        services: list[str] = [],
    ) -> None:
        self._call_backend_app_core(
            *args,
            services=services,
            _out=sys.stdout,
            _err=sys.stderr,
        )

    def _check_config_file(self) -> bool:
        return Path(self.config_file).exists()

    # Check if services item is given
    def _check_services_item(self) -> bool:
        return hasattr(self.config, 'services')

    # set default group main
    def _load_root_services(self) -> None:
        """Load services attribute in the root of the configuration."""
        # must set the default group
        services = self.config.get('services', {})

        if not services:
            return

        self.config['groups'] = {
            'main': {
                'project-name': services.get('project-name'),
                'config-path': services.get('config-path'),
                'env-file': services.get('env-file'),
                'services': {
                    'default': services.get('default'),
                    'available': services.get('available'),
                },
            }
        }
        self.defaults['group'] = 'main'
        self.service_group = deepcopy(self.config['groups']['main'])
        del self.config['services']

    def _filter_service_group(self) -> None:
        groups = self.config['groups']

        if not self.args.get('service_group'):
            default_group = self.defaults.get('group')
            if not default_group:
                SugarLogs.raise_error(
                    'The service group parameter or default '
                    "group configuration weren't defined.",
                    SugarErrorType.SUGAR_INVALID_PARAMETER,
                )
            selected_group_name = default_group
        else:
            selected_group_name = self.args.get('service_group')

        # Verify if project-name is not null
        default_project_name = self.defaults.get('project-name', '') or ''

        for group_name, group_data in groups.items():
            if group_name == selected_group_name:
                if default_project_name and 'project-name' not in group_data:
                    # just use default value if "project-name" is not set
                    group_data['project-name'] = default_project_name
                if not group_data.get('services', {}).get('default'):
                    # if default is not given or it is empty or null,
                    # use as default all the services available
                    default_services = [
                        service['name']
                        for service in group_data.get('services', {}).get(
                            'available'
                        )
                    ]
                    group_data['services']['default'] = ','.join(
                        default_services
                    )
                self.service_group = group_data
                return

        SugarLogs.raise_error(
            f'The given group service "{group_name}" was not found '
            'in the configuration file.',
            SugarErrorType.SUGAR_MISSING_PARAMETER,
        )

    def _load_config(self) -> None:
        with open(self.config_file, 'r') as f:
            # escape template tags
            content = f.read()
            f_content = io.StringIO(content)
            self.config = yaml.safe_load(f_content)

        # check if either  services or  groups are present
        if not (self.config.get('services') or self.config.get('groups')):
            SugarLogs.raise_error(
                'Either `services` OR  `groups` flag must be given',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )
        # check if both services and groups are present
        if self.config.get('services') and self.config.get('groups'):
            SugarLogs.raise_error(
                '`services` and `groups` flags given, only 1 is allowed.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )

    def _load_backend_app(self) -> None:
        backend_cmd = self.config.get('backend', '')
        if backend_cmd.replace(' ', '-') != 'docker-compose':
            SugarLogs.raise_error(
                f'"{self.config["backend"]}" not supported yet.',
                SugarErrorType.SUGAR_COMPOSE_APP_NOT_SUPPORTED,
            )

        if backend_cmd == 'docker-compose':
            self.backend_app = sh.docker_compose
            return
        self.backend_app = sh.docker
        self.backend_args.append('compose')

    def _load_backend_args(self) -> None:
        self._filter_service_group()

        if self.service_group.get('env-file'):
            self.backend_args.extend(
                ['--env-file', self.service_group['env-file']]
            )

        config_path = []
        backend_path_arg = self.service_group['config-path']
        if isinstance(backend_path_arg, str):
            config_path.append(backend_path_arg)
        elif isinstance(backend_path_arg, list):
            config_path.extend(backend_path_arg)
        else:
            SugarLogs.raise_error(
                'The attribute config-path` just supports the data '
                f'types `string` or `list`, {type(backend_path_arg)} '
                'received.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )

        for p in config_path:
            self.backend_args.extend(['--file', p])

        if self.service_group.get('project-name'):
            self.backend_args.extend(
                ['--project-name', self.service_group['project-name']]
            )

    def _load_defaults(self) -> None:
        _defaults = self.config.get('defaults', {})

        for k, v in _defaults.items():
            unescaped_value = v if isinstance(v, str) else str(v)

            _defaults[k] = yaml.safe_load(
                TEMPLATE.from_string(unescaped_value).render(env=self.env)
            )

        self.defaults = _defaults

    def _load_env(self) -> None:
        self.env = dict(os.environ)

        env_file = self.config.get('env-file', '')

        if not env_file:
            return

        if not env_file.startswith('/'):
            # use .sugar file as reference for the working
            # directory for the .env file
            env_file = str(Path(self.config_file).parent / env_file)

        if not Path(env_file).exists():
            SugarLogs.raise_error(
                'The given env-file was not found.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )
        self.env.update(dotenv.dotenv_values(env_file))  # type: ignore

    def _load_service_names(self) -> None:
        services = self.service_group['services']

        if self.args.get('all'):
            self.service_names = [
                v['name']
                for v in self.service_group.get('services', {}).get(
                    'available'
                )
            ]
        elif self.args.get('services') == '':
            SugarLogs.raise_error(
                'If you want to execute the operation for all services, '
                'use --all parameter.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )
        elif self.args.get('services'):
            self.service_names = self.args.get('services', '').split(',')
        elif services.get('default'):
            self.service_names = services.get('default', '').split(',')

    def _verify_args(self) -> None:
        if not self._check_config_file():
            SugarLogs.raise_error(
                'Config file .sugar.yaml not found.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )

        if (
            self.args.get('action')
            and self.args.get('action') not in self.actions
        ):
            SugarLogs.raise_error(
                f'The given action `{self.args.get("action")}` is not '
                f'valid. Use one of them: {",".join(self.actions)}.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )

    def _verify_config(self) -> None:
        if not len(self.config['groups']):
            SugarLogs.raise_error(
                'No service groups found.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )

    def run(self) -> None:
        """Run the given sugar command."""
        action = self.args.get('action', '')
        if not isinstance(action, str):
            SugarLogs.raise_error(
                'The given action is not valid.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )
        getattr(self, f'_cmd_{action.replace("-", "_")}')()

    def _version(self) -> None:
        SugarLogs.print_info(f'Sugar Version: {__version__}')
        SugarLogs.print_info(f'Container Program Path: {self.backend_app}')
        self._call_backend_app('version', services=[])
