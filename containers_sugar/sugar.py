"""
Sugar class for containers

This is the docker-compose commands signature that should be considered:

docker-compose build [options] [SERVICE...]
docker-compose bundle [options]
docker-compose config [options]
docker-compose create [options] [SERVICE...]
docker-compose down [options] [--rmi type] [--volumes] [--remove-orphans]
docker-compose events [options] [SERVICE...]
docker-compose exec [options] SERVICE COMMAND [ARGS...]
docker-compose images [options] [SERVICE...]
docker-compose kill [options] [SERVICE...]
docker-compose logs [options] [SERVICE...]
docker-compose pause [options] SERVICE...
docker-compose port [options] SERVICE PRIVATE_PORT
docker-compose ps [options] [SERVICE...]
docker-compose pull [options] [SERVICE...]
docker-compose push [options] [SERVICE...]
docker-compose restart [options] [SERVICE...]
docker-compose rm [options] [-f | -s] [SERVICE...]
docker-compose run [options] [-p TARGET...] [-v VOLUME...] [-e KEY=VAL...]
    [-l KEY=VAL...] SERVICE [COMMAND] [ARGS...]
docker-compose scale [options] [SERVICE=NUM...]
docker-compose start [options] [SERVICE...]
docker-compose stop [options] [SERVICE...]
docker-compose top [options] [SERVICE...]
docker-compose unpause [options] SERVICE...
docker-compose up [options] [--scale SERVICE=NUM...] [--no-color]
    [--quiet-pull] [SERVICE...]
docker-compose version [options]
"""
import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import sh
import yaml
from colorama import Fore

try:
    from sh import docker_compose
except Exception:
    docker_compose = None


class PrintPlugin:
    def _print_error(self, message: str):
        print(Fore.RED, message, Fore.RESET)

    def _print_info(self, message: str):
        print(Fore.BLUE, message, Fore.RESET)

    def _print_warning(self, message: str):
        print(Fore.YELLOW, message, Fore.RESET)


@dataclass
class SugarBase(PrintPlugin):
    ACTIONS = []

    args: argparse.Namespace = argparse.Namespace()
    config_file: str = ''
    config: dict = {}
    # starts with a simple command
    compose_app: sh.Command = sh.echo
    compose_args: list = []
    options_args: list = []
    cmd_args: list = []
    service_group: dict = {}
    service_names: list = []

    def __init__(
        self,
        args: argparse.Namespace,
        options_args: list = [],
        cmd_args: list = [],
    ):
        self.args = args
        self.options_args = options_args
        self.cmd_args = cmd_args
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
    ):
        sh_extras = {
            '_in': sys.stdin,
            '_out': sys.stdout,
            '_err': sys.stderr,
            '_no_err': True,
            '_env': os.environ,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = (
            self.compose_args
            + list(args)
            + self.options_args
            + services
            + self.cmd_args
        )

        if self.args.verbose:
            print('>>>', self.compose_app, *positional_parameters)
            print('-' * 80)

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

        if self.args.action and self.args.action not in self.ACTIONS:
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

        compose_path = []
        if isinstance(self.service_group['compose-path'], str):
            compose_path.append(self.service_group['compose-path'])
        elif isinstance(self.service_group['compose-path'], list):
            compose_path.extend(self.service_group['compose-path'])
        else:
            self.self._print_error(
                '[EE] The attribute compose-path` supports the data types'
                'string or list.'
            )
            os._exit(1)

        for p in compose_path:
            self.compose_args.extend(['--file', p])

        if self.service_group.get('project-name'):
            self.compose_args.extend(
                ['--project-name', self.service_group['project-name']]
            )

    def _filter_service_group(self):
        groups = self.config['service-groups']

        if not self.args.service_group:
            if len(groups) > 1:
                self._print_error('[EE] The service group was not defined.')
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

    def run(self):
        return getattr(self, f'_{self.args.action.replace("-", "_")}')()


@dataclass
class SugarExt(SugarBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _wait(self):
        self._print_error('[EE] `wait` not implemented yet.')
        os._exit(1)


@dataclass
class SugarMain(SugarBase):
    ACTIONS = [
        'build',
        'config',
        'down',
        'exec',
        'get-ip',
        'logs',
        'pull',
        'run',
        'restart',
        'start',
        'stop',
        'wait',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        if not self.args.service:
            self._print_error(
                '[EE] `exec` sub-command expected --service parameter.'
            )
            os._exit(1)

        self._call_compose_app('exec', services=[self.args.service])

    def _get_ip(self):
        self._print_error('[EE] `get-ip` mot implemented yet.')
        os._exit(1)

    def _logs(self):
        self._call_compose_app('logs', services=self.service_names)

    def _pull(self):
        self._call_compose_app('pull', services=self.service_names)

    def _restart(self):
        options_args = self.options_args
        self.options_args = []
        self._stop()
        self.options_args = options_args
        self._start()

    def _run(self):
        if not self.args.service:
            self._print_error(
                '[EE] `run` sub-command expected --service parameter.'
            )
            os._exit(1)

        self._call_compose_app('run', services=[self.args.service])

    def _start(self):
        self._call_compose_app('up', services=self.service_names)

    def _stop(self):
        self._call_compose_app('stop', services=self.service_names)


class Sugar(PrintPlugin):
    plugins = {}

    def __init__(
        self,
        args: argparse.Namespace,
        options_args: list = [],
        cmd_args: list = [],
    ):
        for klass, name in (
            (SugarMain, 'main'),
            (SugarExt, 'ext'),
        ):
            self.plugins[name] = klass(
                args,
                options_args,
                cmd_args,
            )

        def _version(self):
            self._print_error('Container App Path: ' + str(self.compose_app))
            self._call_compose_app('--version')
