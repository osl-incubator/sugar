"""Sugar class for containers"""
import argparse
import os
import sys
from pathlib import Path

import sh
import yaml
from colorama import Fore

try:
    from sh import docker_compose
except Exception:
    docker_compose = None


class Sugar:
    ACTIONS = [
        'build',
        'config',
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

    args: argparse.Namespace = argparse.Namespace()
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
        cmd: str = '',
    ):
        # note: this is very fragile, we should use a better way to do that
        extras = self.args.extras.split(' ') if self.args.extras else []

        sh_extras = {
            '_in': sys.stdin,
            '_out': sys.stdout,
            '_err': sys.stderr,
            '_no_err': True,
            '_env': os.environ,
        }

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

        p = self.compose_app(
            *positional_parameters,
            **sh_extras,
        )

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            self._print_error(str(e))
            os._exit(1)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            self._print_error(f'[EE] Process {pid} killed.')
            os._exit(1)

    def _check_config_file(self):
        return Path(self.config_file).exists()

    def _verify_args(self):
        if not self._check_config_file():
            self._print_error(
                '[EE] Config file .containers-sugar.yaml not found.'
            )
            os._exit(1)

        if self.args.action not in self.ACTIONS:
            self._print_error(
                '[EE] The given action is not valid. Use one of them: '
                + ','.join(self.ACTIONS)
            )
            os._exit(1)

    def _verify_config(self):
        if not len(self.config['service-groups']):
            self._print_error('[EE] No service groups found.')
            os._exit(1)

    def _load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def _load_compose_app(self):
        if self.config['compose-app'] == 'docker-compose':
            self.compose_app = docker_compose
        else:
            self._print_error(
                f'[EE] "{self.config["compose-app"]}" not supported yet.'
            )
            os._exit(1)

        if self.compose_app is None:
            self._print_error(
                f'[EE] "{self.config["compose-app"]}" not found.'
            )
            os._exit(1)

    def _load_compose_args(self):
        self._filter_service_group()

        if 'env-file' in self.service_group:
            self.compose_args.extend(
                ['--env-file', self.service_group['env-file']]
            )

        service_group = []
        if isinstance(self.service_group['compose-path'], str):
            service_group.append(self.service_group['compose-path'])
        elif isinstance(self.service_group['compose-path'], list):
            service_group.extend(self.service_group['compose-path'])
        else:
            self.self._print_error(
                '[EE] The attribute compose-path` supports the data types'
                'string or list.'
            )
            os._exit(1)

        for p in service_group:
            self.compose_args.extend(['--file', p])

        if self.service_group.get('project-name'):
            self.compose_args.extend(
                ['--project-name', self.service_group['project-name']]
            )

    def _filter_service_group(self):
        groups = self.config['service-groups']

        if not self.args.service_group:
            if len(groups) > 1:
                self._print_error(
                    '[EE] Unable to infer the service group:'
                    'The service group for this operation was not defined, '
                    'and there are more than one service group in the '
                    'configuration file.'
                )
                os._exit(1)
            self.service_group = groups[0]
            return

        group_name = self.args.service_group
        for g in groups:
            if g['name'] == group_name:
                self.service_group = g
                return

        self._print_error(
            f'[EE] The given group service "{group_name}" was not found '
            'in the configuration file.'
        )
        os._exit(1)

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

    # print messages

    def _print_error(self, message: str):
        print(Fore.RED, message, Fore.RESET)

    def _print_info(self, message: str):
        print(Fore.BLUE, message, Fore.RESET)

    def _print_warning(self, message: str):
        print(Fore.YELLOW, message, Fore.RESET)

    # container commands
    def _config(self):
        self._call_compose_app('config')

    def _build(self):
        self._call_compose_app('build', services=self.service_names)

    def _down(self):
        if self.args.all or self.args.services:
            self._print_error(
                "[EE] The `down` sub-command doesn't accept `--all` "
                'neither `--services` parameters.'
            )
            os._exit(1)

        self._call_compose_app(
            'down',
            '--remove-orphans',
            services=[],
        )

    def _exec(self):
        if len(self.service_names) > 1:
            self._print_error(
                '[EE] `exec` sub-command expected just one service as '
                'parameter'
            )
            os._exit(1)

        self._call_compose_app(
            'exec',
            services=self.service_names,
            cmd=self.args.cmd,
        )

    def _get_ip(self):
        self._print_error('[EE] `get-ip` mot implemented yet.')
        os._exit(1)

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
            self._print_error(
                '[EE] `run` sub-command expected just one service as '
                'parameter'
            )
            os._exit(1)

        self._call_compose_app(
            'run',
            services=self.service_names,
            cmd=self.args.cmd,
        )

    def _start(self):
        self._call_compose_app('up', '-d', services=self.service_names)

    def _stop(self):
        self._call_compose_app('stop', services=self.service_names)

    def _wait(self):
        self._print_error('[EE] `wait` not implemented yet.')
        os._exit(1)

    def _version(self):
        self._print_error('Container App Path: ' + str(self.compose_app))
        self._call_compose_app('--version')

    def run(self):
        return getattr(self, f'_{self.args.action.replace("-", "_")}')()
