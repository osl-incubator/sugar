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

from jinja2 import Template

from sugar.logs import KxgrErrorType, KxgrLogs


def escape_template_tag(v: str) -> str:
    """Escape template tags for template rendering."""
    return v.replace('{{', r'\{\{').replace('}}', r'\}\}')


def unescape_template_tag(v: str) -> str:
    """Unescape template tags for template rendering."""
    return v.replace(r'\{\{', '{{').replace(r'\}\}', '}}')


class SugarBase:
    """SugarBase defined the base structure for the Sugar classes."""

    actions: list[str] = []
    args: dict = {}
    config_file: str = ''
    config: dict = {}
    # note: it starts with a simple command
    #       it is replaced later in the execution
    compose_app: sh.Command = sh.echo
    compose_args: list = []
    defaults: dict = {}
    env: dict = {}
    options_args: list = []
    cmd_args: list = []
    service_group: dict = {}
    service_names: list = []

    def __init__(
        self,
        args: dict,
        options_args: list = [],
        cmd_args: list = [],
    ):
        """Initialize SugarBase instance."""
        self.args = deepcopy(args)
        self.options_args = deepcopy(options_args)
        self.cmd_args = deepcopy(cmd_args)
        self.config_file = self.args.get('config_file', '')
        self.config = dict()
        self.compose_args = list()
        self.defaults = dict()
        self.env = dict()
        self.service_group = dict()
        self.service_names = list()

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
        *args,
        services: list = [],
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
            KxgrLogs.raise_error(str(e), KxgrErrorType.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            KxgrLogs.raise_error(
                f'Process {pid} killed.', KxgrErrorType.SH_KEYBOARD_INTERRUPT
            )

    def _call_compose_app(
        self,
        *args,
        services: list = [],
    ) -> None:
        self._call_compose_app_core(
            *args,
            services=services,
            _out=sys.stdout,
            _err=sys.stderr,
        )

    def _check_config_file(self):
        return Path(self.config_file).exists()

    # Check if services item is given
    def _check_services_item(self):
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

    def _filter_service_group(self):
        groups = self.config['groups']

        if not self.args.get('service_group'):
            default_group = self.defaults.get('group')
            if not default_group:
                KxgrLogs.raise_error(
                    'The service group parameter or default '
                    "group configuration weren't defined.",
                    KxgrErrorType.KXGR_INVALID_PARAMETER,
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

        KxgrLogs.raise_error(
            f'The given group service "{group_name}" was not found '
            'in the configuration file.',
            KxgrErrorType.KXGR_MISSING_PARAMETER,
        )

    def _load_config(self):
        with open(self.config_file, 'r') as f:
            # escape template tags
            content = escape_template_tag(f.read())
            f_content = io.StringIO(content)
            self.config = yaml.safe_load(f_content)

        # check if either  services or  groups are present
        if not (self.config.get('services') or self.config.get('groups')):
            KxgrLogs.raise_error(
                'Either `services` OR  `groups` flag must be given',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )
        # check if both services and groups are present
        if self.config.get('services') and self.config.get('groups'):
            KxgrLogs.raise_error(
                '`services` and `groups` flags given, only 1 is allowed.',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )

    def _load_compose_app(self):
        compose_cmd = self.config.get('compose-app', '')
        if compose_cmd.replace(' ', '-') != 'docker-compose':
            KxgrLogs.raise_error(
                f'"{self.config["compose-app"]}" not supported yet.',
                KxgrErrorType.KXGR_COMPOSE_APP_NOT_SUPPORTED,
            )

        if compose_cmd == 'docker-compose':
            self.compose_app = sh.docker_compose
            return
        self.compose_app = sh.docker
        self.compose_args.append('compose')

    def _load_compose_args(self):
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
            self.KxgrLogs.raise_error(
                'The attribute compose-path` just supports the data '
                f'types `string` or `list`, {type(compose_path_arg)} '
                'received.',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )

        for p in compose_path:
            self.compose_args.extend(['--file', p])

        if self.service_group.get('project-name'):
            self.compose_args.extend(
                ['--project-name', self.service_group['project-name']]
            )

    def _load_defaults(self):
        _defaults = self.config.get('defaults', {})

        for k, v in _defaults.items():
            unescaped_value = (
                unescape_template_tag(v) if isinstance(v, str) else str(v)
            )

            _defaults[k] = yaml.safe_load(
                Template(unescaped_value).render(env=self.env)
            )

        self.defaults = _defaults

    def _load_env(self):
        self.env = dict(os.environ)

        env_file = self.config.get('env-file', '')

        if not env_file:
            return

        if not env_file.startswith('/'):
            # use .sugar file as reference for the working
            # directory for the .env file
            env_file = str(Path(self.config_file).parent / env_file)

        if not Path(env_file).exists():
            KxgrLogs.raise_error(
                'The given env-file was not found.',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )
        self.env.update(dotenv.dotenv_values(env_file))

    def _load_service_names(self):
        services = self.service_group['services']

        if self.args.get('all'):
            self.service_names = [
                v['name']
                for v in self.service_group.get('services', {}).get(
                    'available'
                )
            ]
        elif self.args.get('services') == '':
            KxgrLogs.raise_error(
                'If you want to execute the operation for all services, '
                'use --all parameter.',
                KxgrErrorType.KXGR_INVALID_PARAMETER,
            )
        elif self.args.get('services'):
            self.service_names = self.args.get('services').split(',')
        elif services.get('default'):
            self.service_names = services['default'].split(',')

    def _verify_args(self):
        if not self._check_config_file():
            KxgrLogs.raise_error(
                'Config file .sugar.yaml not found.',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )

        if (
            self.args.get('action')
            and self.args.get('action') not in self.actions
        ):
            KxgrLogs.raise_error(
                f'The given action `{self.args.get("action")}` is not '
                f'valid. Use one of them: {",".join(self.actions)}.',
                KxgrErrorType.KXGR_INVALID_PARAMETER,
            )

    def _verify_config(self):
        if not len(self.config['groups']):
            KxgrLogs.raise_error(
                'No service groups found.',
                KxgrErrorType.KXGR_INVALID_CONFIGURATION,
            )

    def run(self):
        """Run the given sugar command."""
        action = self.args.get('action')
        if not isinstance(action, str):
            KxgrLogs.raise_error(
                'The given action is not valid.',
                KxgrErrorType.KXGR_INVALID_PARAMETER,
            )
        return getattr(self, f'_{action.replace("-", "_")}')()


class SugarDockerCompose(SugarBase):
    """
    SugarDockerCompose provides the docker compose commands.

    This are the commands that is currently provided:

        build [options] [SERVICE...]
        config [options]
        create [options] [SERVICE...]
        down [options] [--rmi type] [--volumes] [--remove-orphans]
        events [options] [SERVICE...]
        exec [options] SERVICE COMMAND [ARGS...]
        images [options] [SERVICE...]
        kill [options] [SERVICE...]
        logs [options] [SERVICE...]
        pause [options] SERVICE...
        port [options] SERVICE PRIVATE_PORT
        ps [options] [SERVICE...]
        pull [options] [SERVICE...]
        push [options] [SERVICE...]
        restart [options] [SERVICE...]
        rm [options] [-f | -s] [SERVICE...]
        run [options] [-p TARGET...] [-v VOLUME...] [-e KEY=VAL...]
            [-l KEY=VAL...] SERVICE [COMMAND] [ARGS...]
        start [options] [SERVICE...]
        stop [options] [SERVICE...]
        top [options] [SERVICE...]
        unpause [options] SERVICE...
        up [options] [--scale SERVICE=NUM...] [--no-color]
            [--quiet-pull] [SERVICE...]
        version [options]
    """

    actions: list[str] = [
        'build',
        'config',
        'create',
        'down',
        'events',
        'exec',
        'images',
        'kill',
        'logs',
        'pause',
        'port',
        'ps',
        'pull',
        'push',
        'restart',
        'rm',
        'run',
        'start',
        'stop',
        'top',
        'unpause',
        'up',
        'version',
    ]

    def __init__(self, *args, **kwargs):
        """Initialize SugarDockerCompose instance."""
        super().__init__(*args, **kwargs)

    # container commands
    def _build(self):
        self._call_compose_app('build', services=self.service_names)

    def _config(self):
        self._call_compose_app('config', services=self.service_names)

    def _create(self):
        self._call_compose_app('create', services=self.service_names)

    def _down(self):
        if self.args.get('all') or self.args.get('services'):
            KxgrLogs.raise_error(
                "The `down` sub-command doesn't accept `--all` "
                'neither `--services` parameters.',
                KxgrErrorType.KXGR_INVALID_PARAMETER,
            )

        self._call_compose_app(
            'down',
            '--remove-orphans',
            services=[],
        )

    def _events(self):
        # port is not complete supported
        if not self.args.get('service'):
            KxgrLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                KxgrErrorType.KXGR_MISSING_PARAMETER,
            )
        self._call_compose_app('events', services=[self.args.get('service')])

    def _exec(self):
        if not self.args.get('service'):
            KxgrLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                KxgrErrorType.KXGR_MISSING_PARAMETER,
            )

        self._call_compose_app('exec', services=[self.args.get('service')])

    def _images(self):
        self._call_compose_app('images', services=self.service_names)

    def _kill(self):
        self._call_compose_app('kill', services=self.service_names)

    def _logs(self):
        self._call_compose_app('logs', services=self.service_names)

    def _pause(self):
        self._call_compose_app('pause', services=self.service_names)

    def _port(self):
        # port is not complete supported
        if not self.args.get('service'):
            KxgrLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                KxgrErrorType.KXGR_MISSING_PARAMETER,
            )
        # TODO: check how private port could be passed
        self._call_compose_app('port', services=[self.args.get('service')])

    def _ps(self):
        self._call_compose_app('ps', services=self.service_names)

    def _pull(self):
        self._call_compose_app('pull', services=self.service_names)

    def _push(self):
        self._call_compose_app('push', services=self.service_names)

    def _restart(self):
        self._call_compose_app('restart', services=self.service_names)

    def _rm(self):
        self._call_compose_app('rm', services=self.service_names)

    def _run(self):
        if not self.args.get('service'):
            KxgrLogs.raise_error(
                '`run` sub-command expected --service parameter.',
                KxgrErrorType.KXGR_MISSING_PARAMETER,
            )

        self._call_compose_app('run', services=[self.args.get('service')])

    def _start(self):
        self._call_compose_app('start', services=self.service_names)

    def _stop(self):
        self._call_compose_app('stop', services=self.service_names)

    def _top(self):
        self._call_compose_app('top', services=self.service_names)

    def _unpause(self):
        self._call_compose_app('unpause', services=self.service_names)

    def _up(self):
        self._call_compose_app('up', services=self.service_names)

    def _version(self):
        self._call_compose_app('version', services=[])
