"""Sugar class for containers"""
import os
import sys
from pathlib import Path
from typing import Optional

import sh
import yaml

try:
    from sh import docker_compose
except Exception:
    docker_compose = None


class Sugar:
    ACTIONS = [
        'build',
        'down',
        'exec',
        'get-ip',
        'logs',
        'logs-follow',
        'pull',
        'run',
        'restart',
        'start',
        'stop',
        'version',
        'wait',
    ]

    args: Optional[object] = None
    config_file: str = ''
    config: dict = {}
    # starts with a simple command
    compose_app: sh.Command = sh.echo
    compose_args: list = []
    service_group: dict = {}
    service_names: list = []

    def __init__(self, args):
        self.args = args
        self.config_file = self.args.config_file
        self._load_config()
        self._verify_args()
        self._load_compose_app()

    def load_services(self):
        self._load_compose_args()
        self._verify_config()
        self._load_service_names()

    def _call_compose_app(
        self,
        *args,
        services: list = [],
        extras: list = [],
        cmd: str = '',
    ):
        sh_extras = {
            '_in': sys.stdin,
            '_out': sys.stdout,
            '_err': sys.stderr,
            '_no_err': True,
            '_env': os.environ,
        }

        run_in_bg = False
        if args[0] in ['start', 'restart']:
            run_in_bg = True
            sh_extras.update(
                {
                    '_bg': True,
                    '_bg_exc': False,
                }
            )

        cmd_list = [cmd] if cmd else []

        print(
            '>>>',
            self.compose_app,
            *self.compose_args,
            *args,
            *extras,
            *services,
            *cmd_list,
        )
        print('-' * 80)

        positional_parameters = (
            self.compose_args + list(args) + extras + services + cmd_list
        )

        if not run_in_bg:
            try:
                self.compose_app(
                    *positional_parameters,
                    **sh_extras,
                )
            except sh.ErrorReturnCode as e:
                print(e)
                exit(1)
            return

        p = self.compose_app(
            *positional_parameters,
            **sh_extras,
        )

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            print(e)
            exit(1)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            print(f'[WW] Process {pid} killed.')

    def _check_config_file(self):
        return Path(self.config_file).exists()

    def _verify_args(self):
        if not self._check_config_file():
            print('[EE] Config file .containers-sugar.yaml not found.')
            exit(1)

        if self.args.action not in self.ACTIONS:
            print(
                '[EE] The given action is not valid. Use one of them: '
                + ','.join(self.ACTIONS)
            )
            exit(1)

    def _verify_config(self):
        if not len(self.config['service-groups']):
            print('[EE] No service groups found.')
            exit(1)

    def _load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def _load_compose_app(self):
        if self.config['compose-app'] == 'docker-compose':
            self.compose_app = docker_compose
        else:
            print(f'[EE] "{self.config["compose-app"]}" not supported yet.')
            exit(1)

        if self.compose_app is None:
            print(f'[EE] "{self.config["compose-app"]}" not found.')
            exit(1)

    def _load_compose_args(self):
        self._filter_service_group()

        if 'env-file' in self.service_group:
            self.compose_args.extend(
                ['--env-file', self.service_group['env-file']]
            )

        self.compose_args.extend(
            ['--file', self.service_group['compose-path']]
        )

        if 'project-name' in self.service_group:
            self.compose_args.extend(
                ['--project-name', self.service_group['project-name']]
            )

    def _filter_service_group(self):
        groups = self.config['service-groups']

        if not self.args.service_group:
            if len(groups) > 1:
                print(
                    '[EE] Unable to infer the service group:'
                    'The service group for this operation was not defined, '
                    'and there are more than one service group in the '
                    'configuration file.'
                )
                exit(1)
            self.service_group = groups[0]
            return

        group_name = self.args.service_group
        for g in groups:
            if g['name'] == group_name:
                self.service_group = g
                return

        print(
            f'[EE] The given group service "{group_name}" was not found '
            'in the configuration file.'
        )
        exit(1)

    def _load_service_names(self):
        services = self.service_group['services']

        if self.args.all:
            self.service_names = [
                v['name']
                for v in self.service_group.get('services', {}).get('list')
            ]
        elif self.args.services == '':
            pass
        elif self.args.services:
            self.service_names = self.args.services.split(',')
        elif 'default' in services and services['default']:
            self.service_names = services['default'].split(',')

    # container commands

    def _build(self):
        self._call_compose_app('build', services=self.service_names)

    def _down(self):
        self._call_compose_app(
            'down',
            '--volumes',
            '--remove-orphans',
            services=self.service_names,
        )

    def _exec(self):
        if len(self.service_names) > 1:
            print(
                '[EE] `exec` sub-command expected just one service as '
                'parameter'
            )
            exit(1)
        # note: this is very fragile, we should use a better way to do that
        extras = self.args.extras.split(' ') if self.args.extras else []

        self._call_compose_app(
            'exec',
            services=self.service_names,
            extras=extras,
            cmd=self.args.cmd,
        )

    def _get_ip(self):
        print('[EE] `get-ip` mot implemented yet.')
        exit(1)

    def _logs(self):
        self._call_compose_app('logs', services=self.service_names)

    def _logs_follow(self):
        self._call_compose_app('logs', '--follow', services=self.service_names)

    def _pull(self):
        self._call_compose_app('pull', services=self.service_names)

    def _restart(self):
        self._stop()
        self._start()

    def _run(self):
        if len(self.service_names) > 1:
            print(
                '[EE] `run` sub-command expected just one service as '
                'parameter'
            )
            exit(1)
        # note: this is very fragile, we should use a better way to do that
        extras = self.args.extras.split(' ')
        self._call_compose_app(
            'run',
            services=self.service_names,
            extras=extras,
            cmd=self.args.cmd,
        )

    def _start(self):
        self._call_compose_app('up', '-d', services=self.service_names)

    def _stop(self):
        self._call_compose_app('stop', services=self.service_names)

    def _wait(self):
        print('[EE] `wait` not implemented yet.')
        exit(1)

    def _version(self):
        print('Container App Path: ', self.compose_app)
        self._call_compose_app('--version')

    def run(self):
        return getattr(self, f'_{self.args.action.replace("-", "_")}')()
