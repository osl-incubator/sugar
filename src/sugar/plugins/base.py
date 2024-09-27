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
    compose_app: sh.Command = sh.echo
    compose_args: list[str] = []
    defaults: dict[str, Any] = {}
    env: dict[str, str] = {}
    options_args: list[str] = []
    cmd_args: list[str] = []
    service_group: dict[str, Any] = {}
    service_names: list[str] = []

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
        self.compose_args: list[str] = []
        self.defaults: dict[str, Any] = {}
        self.env: dict[str, str] = {}
        self.service_group: dict[str, Any] = {}
        self.service_names: list[str] = []

        self._load_config()
        self._load_env()
        self._load_defaults()
        self._load_root_services()
        self._verify_args()
        self._load_compose_app()
        self._load_compose_args()
        self._verify_config()
        self._load_service_names()

    def _call_compose_app_core(
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
            self.compose_args
            + list(args)
            + (options_args or self.options_args)
            + services
            + (cmd_args or self.cmd_args)
        )

        if self.args.get('verbose'):
            print('>>>', self.compose_app, *positional_parameters)
            print('-' * 80)

        p = self.compose_app(
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

    def _call_compose_app(
        self,
        *args: str,
        services: list[str] = [],
    ) -> None:
        self._call_compose_app_core(
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
                'compose-path': services.get('compose-path'),
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

    def _load_compose_app(self) -> None:
        compose_cmd = self.config.get('compose-app', '')
        if compose_cmd.replace(' ', '-') != 'docker-compose':
            SugarLogs.raise_error(
                f'"{self.config["compose-app"]}" not supported yet.',
                SugarErrorType.SUGAR_COMPOSE_APP_NOT_SUPPORTED,
            )

        if compose_cmd == 'docker-compose':
            self.compose_app = sh.docker_compose
            return
        self.compose_app = sh.docker
        self.compose_args.append('compose')

    def _load_compose_args(self) -> None:
        self._filter_service_group()

        if self.service_group.get('env-file'):
            self.compose_args.extend(
                ['--env-file', self.service_group['env-file']]
            )

        compose_path = []
        compose_path_arg = self.service_group['compose-path']
        if isinstance(compose_path_arg, str):
            compose_path.append(compose_path_arg)
        elif isinstance(compose_path_arg, list):
            compose_path.extend(compose_path_arg)
        else:
            SugarLogs.raise_error(
                'The attribute compose-path` just supports the data '
                f'types `string` or `list`, {type(compose_path_arg)} '
                'received.',
                SugarErrorType.SUGAR_INVALID_CONFIGURATION,
            )

        for p in compose_path:
            self.compose_args.extend(['--file', p])

        if self.service_group.get('project-name'):
            self.compose_args.extend(
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
        getattr(self, f'_{action.replace("-", "_")}')()

    def _version(self) -> None:
        SugarLogs.print_info(f'Sugar Version: {__version__}')
        SugarLogs.print_info(f'Container Program Path: {self.compose_app}')
        self._call_compose_app('version', services=[])


class SugarDockerCompose(SugarBase):
    """
    SugarDockerCompose provides the docker compose commands.

    This are the commands that is currently provided:

        attach [options] SERVICE
        build [options] [SERVICE...]
        config [options] [SERVICE...]
        cp:
          - cp [options] SERVICE:SRC_PATH DEST_PATH|-
          - cp [options] SRC_PATH|- SERVICE:DEST_PATH
        create [options] [SERVICE...]
        down [options] [--rmi type] [--volumes] [--remove-orphans]
        events [options] [SERVICE...]
        exec [options] SERVICE COMMAND [ARGS...]
        images [options] [SERVICE...]
        kill [options] [SERVICE...]
        logs [options] [SERVICE...]
        ls [options]
        pause [options] SERVICE...
        port [options] SERVICE PRIVATE_PORT
        ps [options] [SERVICE...]
        pull [options] [SERVICE...]
        push [options] [SERVICE...]
        restart [options] [SERVICE...]
        rm [options] [-f | -s] [SERVICE...]
        run [options] [-p TARGET...] [-v VOLUME...] [-e KEY=VAL...]
            [-l KEY=VAL...] SERVICE [COMMAND] [ARGS...]
        scale [SERVICE=REPLICAS...]
        start [options] [SERVICE...]
        # todo: implement stats
        # stats [options] [SERVICE]
        stop [options] [SERVICE...]
        top [options] [SERVICE...]
        unpause [options] [SERVICE...]
        up [options] [--scale SERVICE=NUM...] [--no-color]
            [--quiet-pull] [SERVICE...]
        version [options]
        wait SERVICE [SERVICE...] [options]
        watch [SERVICE...]
    """

    actions: list[str] = [
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
        'ls',
        'logs',
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
        'stats',
        'stop',
        'top',
        'unpause',
        'up',
        'version',
        'wait',
        'watch',
    ]

    def __init__(
        self,
        args: dict[str, str],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
    ):
        """Initialize SugarDockerCompose instance."""
        super().__init__(args, options_args=options_args, cmd_args=cmd_args)

    # container commands
    def _attach(self) -> None:
        service_name = self.args.get('service', '')
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_compose_app('attach', services=service_name_list)

    def _build(self) -> None:
        self._call_compose_app('build', services=self.service_names)

    def _config(self) -> None:
        self._call_compose_app('config', services=self.service_names)

    def _cp(self) -> None:
        self._call_compose_app('cp', services=[])

    def _create(self) -> None:
        self._call_compose_app('create', services=self.service_names)

    def _down(self) -> None:
        if self.args.get('all') or self.args.get('services'):
            SugarLogs.raise_error(
                "The `down` sub-command doesn't accept `--all` "
                'neither `--services` parameters.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )

        self._call_compose_app(
            'down',
            '--remove-orphans',
            services=[],
        )

    def _events(self) -> None:
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list = [service_name] if service_name else []
        self._call_compose_app('events', services=service_name_list)

    def _exec(self) -> None:
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )

        service_name_list: list[str] = [service_name] if service_name else []
        self._call_compose_app('exec', services=service_name_list)

    def _images(self) -> None:
        self._call_compose_app('images', services=self.service_names)

    def _kill(self) -> None:
        self._call_compose_app('kill', services=self.service_names)

    def _logs(self) -> None:
        self._call_compose_app('logs', services=self.service_names)

    def _ls(self) -> None:
        self._call_compose_app('ls', services=[])

    def _pause(self) -> None:
        self._call_compose_app('pause', services=self.service_names)

    def _port(self) -> None:
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        # TODO: check how private port could be passed
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_compose_app('port', services=service_name_list)

    def _ps(self) -> None:
        self._call_compose_app('ps', services=self.service_names)

    def _pull(self) -> None:
        self._call_compose_app('pull', services=self.service_names)

    def _push(self) -> None:
        self._call_compose_app('push', services=self.service_names)

    def _restart(self) -> None:
        self._call_compose_app('restart', services=self.service_names)

    def _rm(self) -> None:
        self._call_compose_app('rm', services=self.service_names)

    def _run(self) -> None:
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`run` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_compose_app('run', services=service_name_list)

    def _scale(self) -> None:
        self._call_compose_app('ls', services=[])

    def _start(self) -> None:
        self._call_compose_app('start', services=self.service_names)

    def _stop(self) -> None:
        self._call_compose_app('stop', services=self.service_names)

    def _top(self) -> None:
        self._call_compose_app('top', services=self.service_names)

    def _unpause(self) -> None:
        self._call_compose_app('unpause', services=self.service_names)

    def _up(self) -> None:
        self._call_compose_app('up', services=self.service_names)

    def _wait(self) -> None:
        self._call_compose_app('wait', services=self.service_names)

    def _watch(self) -> None:
        self._call_compose_app('watch', services=self.service_names)
