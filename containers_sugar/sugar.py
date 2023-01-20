"""Sugar class for containers"""
import sys
from pathlib import Path

import yaml

try:
    from sh import docker_compose
except Exception:
    docker_compose = None

try:
    from sh import podman_compose
except Exception:
    podman_compose = None


class Sugar:
    ACTIONS = [
        'build',
        'down',
        'get-ip',
        'logs',
        'logs-follow',
        'pull',
        'restart',
        'start',
        'stop',
        'wait',
    ]

    args: object | None = None
    config_file: str = ''
    config: dict = {}
    compose_app: object | None = None
    compose_args: list = []
    service_group: dict = {}
    service_names: list = []

    def __init__(self, args):
        self.args = args

        self.config_file = self.args.config_file

        self._verify_args()
        self._load_config()
        self._verify_config()
        self._load_compose_app()
        self._load_compose_args()
        self._load_service_names()

    def _call_compose_app(self, *args):
        return self.compose_app(
            *self.compose_args,
            *args,
            *self.service_names,
            _out=sys.stdout,
            _err=sys.stderr,
        )

    def _check_config_file(self):
        return Path(self.config_file).exists()

    def _verify_args(self):
        if not self._check_config_file():
            raise Exception(
                '[config] Config file .containers-sugar.yaml not found.'
            )

        if self.args.action not in self.ACTIONS:
            raise Exception(
                'The given action is not valid. Use one of them: '
                + ','.join(self.ACTIONS)
            )

    def _verify_config(self):
        if not len(self.config['service-groups']):
            raise Exception('No service groups found.')

    def _load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def _load_compose_app(self):
        if self.config['compose-app'] == 'docker-compose':
            self.compose_app = docker_compose
        elif self.config['compose-app'] == 'podman-compose':
            self.compose_app = podman_compose
        else:
            raise Exception(
                f'"{self.config["compose-app"]}" not supported yet.'
            )

        if self.compose_app is None:
            raise Exception(f'"{self.config["compose-app"]}" not found.')

    def _filter_service_group(self):
        groups = self.config['service-groups']

        if not self.args.service_group:
            if len(groups) > 1:
                raise Exception(
                    'Unable to infer the service group:'
                    'The service group for this operation was not defined, '
                    'and there are more than one service group in the '
                    'configuration file.'
                )
            self.service_group = groups[0]
            return

        group_name = self.args.service_group
        for g in groups:
            if g['name'] == group_name:
                self.service_group = g
                return

        raise Exception(
            f'The given group service "{group_name}" was not found in the '
            'configuration file.'
        )

    def _load_compose_args(self):
        self._filter_service_group()

        if hasattr(self.service_group, 'env-file'):
            self.compose_args.extend(
                ['--env-file', self.service_group['env-file']]
            )

        self.compose_args.extend(
            ['--file', self.service_group['compose-path']]
        )

    def _load_service_names(self):
        services = self.service_group['services']

        if self.args.services == '':
            pass
        elif self.args.services:
            self.service_names = self.args.services.split(',')
        elif 'default' in services and services['default']:
            self.service_names = services['default'].split(',')

    # container commands

    def _build(self):
        self._call_compose_app('build')

    def _down(self):
        self._call_compose_app('down', '--volumes', '--remove-orphans')

    def _get_ip(self):
        print('get_ip')

    def _logs(self):
        self._call_compose_app('logs')

    def _logs_follow(self):
        self._call_compose_app('logs', '--follow')

    def _pull(self):
        self._call_compose_app('pull')

    def _restart(self):
        self._stop()
        self._start()

    def _start(self):
        self._call_compose_app('up', '-d')

    def _stop(self):
        self._call_compose_app('stop')

    def _wait(self):
        print('wait')

    def run(self):
        return getattr(self, f'_{self.args.action.replace("-", "_")}')()
