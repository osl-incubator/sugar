"""
Sugar class for containers.
"""
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

import sh
import yaml
from colorama import Fore

try:
    from sh import docker_compose
except Exception:
    docker_compose = None

from containers_sugar import __version__


class PrintPlugin:
    def _print_error(self, message: str):
        print(Fore.RED, message, Fore.RESET)

    def _print_info(self, message: str):
        print(Fore.BLUE, message, Fore.RESET)

    def _print_warning(self, message: str):
        print(Fore.YELLOW, message, Fore.RESET)


class SugarBase(PrintPlugin):
    actions: List[str] = []
    args: dict = {}
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
        args: dict,
        options_args: list = [],
        cmd_args: list = [],
    ):
        self.args = deepcopy(args)
        self.options_args = deepcopy(options_args)
        self.cmd_args = deepcopy(cmd_args)
        self.config_file = self.args.get('config_file', '')
        self.config = dict()
        self.compose_args = list()
        self.service_group = dict()
        self.service_names = list()

        self._load_config()
        self._verify_args()
        self._load_compose_app()
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

        if (
            self.args.get('action')
            and self.args.get('action') not in self.actions
        ):
            self._print_error(
                f'[EE] The given action `{self.args.get("action")}` is not '
                f'valid. Use one of them: {",".join(self.actions)}.'
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

        if not self.args.get('service_group'):
            if len(groups) > 1:
                self._print_error('[EE] The service group was not defined.')
                os._exit(1)
            self.service_group = groups[0]
            return

        group_name = self.args.get('service_group')
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

        if self.args.get('all'):
            self.service_names = [
                v['name']
                for v in self.service_group.get('services', {}).get('list')
            ]
        elif self.args.get('services') == '':
            self._print_error(
                'If you want to execute the operation for all services, '
                'use --all parameter.'
            )
            os._exit(1)
        elif self.args.get('services'):
            self.service_names = self.args.get('services').split(',')
        elif 'default' in services and services['default']:
            self.service_names = services['default'].split(',')

    def run(self):
        action = self.args.get('action')
        if not isinstance(action, str):
            self._print_error('The given action is not valid.')
            os._exit(1)
        return getattr(self, f'_{action.replace("-", "_")}')()


class SugarDockerCompose(SugarBase):
    """
    This is the docker-compose commands that is implemented:

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

    actions: List[str] = [
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
        super().__init__(*args, **kwargs)

    # container commands
    def _build(self):
        self._call_compose_app('build', services=self.service_names)

    def _config(self):
        self._call_compose_app('config')

    def _create(self):
        self._call_compose_app('create', services=self.service_names)

    def _down(self):
        if self.args.get('all') or self.args.get('services'):
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

    def _events(self):
        self._call_compose_app('events', services=self.service_names)

    def _exec(self):
        if not self.args.get('service'):
            self._print_error(
                '[EE] `exec` sub-command expected --service parameter.'
            )
            os._exit(1)

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
        # TODO: check how private port could be passed
        self._call_compose_app('port', services=self.service_names)

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
            self._print_error(
                '[EE] `run` sub-command expected --service parameter.'
            )
            os._exit(1)

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
        self._call_compose_app('version', services=self.service_names)


class SugarExt(SugarDockerCompose):
    def __init__(self, *args, **kwargs):
        self.actions += [
            'get-ip',
            'restart',
            'start',
            'wait',
        ]

        super().__init__(*args, **kwargs)

    def _get_ip(self):
        self._print_error('[EE] `get-ip` mot implemented yet.')
        os._exit(1)

    def _restart(self):
        options = self.options_args
        self.options_args = []
        self._stop()
        self.options_args = options
        self._start()

    def _start(self):
        self._up()

    def _wait(self):
        self._print_error('[EE] `wait` not implemented yet.')
        os._exit(1)


class Sugar(SugarBase, PrintPlugin):
    plugins_definition: Dict[str, type] = {
        'main': SugarDockerCompose,
        'ext': SugarExt,
    }
    plugin: Optional[SugarBase] = None

    def __init__(
        self,
        args: dict,
        options_args: list = [],
        cmd_args: list = [],
    ):
        plugin_name = args.get('plugin', '')

        use_plugin = not (plugin_name == 'main' and not args.get('action'))

        if (
            plugin_name
            and plugin_name not in self.plugins_definition
            and not args.get('action')
        ):
            args['action'] = plugin_name
            args['plugin'] = 'main'

        # update plugin name
        plugin_name = args.get('plugin', '')

        super().__init__(args, options_args, cmd_args)

        if not use_plugin:
            return

        self.plugin = self.plugins_definition[plugin_name](
            args,
            options_args,
            cmd_args,
        )

    def _verify_args(self):
        if self.args.get('plugin') not in self.plugins_definition:
            plugins_name = [k for k in self.plugins_definition.keys()]

            self._print_error(
                f'[EE] `plugin` parameter `{ self.args.get("plugin") }` '
                f'not found. Options: { plugins_name }.'
            )
            os._exit(1)

    def get_actions(self):
        actions = []

        for k, v in self.plugins_definition.items():
            actions.extend(v.actions)

        return actions

    def _load_compose_args(self):
        pass

    def _load_service_names(self):
        pass

    def run(self):
        if self.args['version']:
            return self._version()

        if not self.args.get('action'):
            return

        return self.plugin.run()

    # actions available

    def _version(self):
        self._print_info('containers-sugar version:' + str(__version__))
        self._print_info('container program path: ' + str(self.compose_app))
        self._call_compose_app('--version')
