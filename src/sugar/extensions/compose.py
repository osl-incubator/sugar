"""Sugar plugin for docker compose."""

from __future__ import annotations

from sugar.extensions.base import SugarBase
from sugar.logs import SugarErrorType, SugarLogs


class SugarCompose(SugarBase):
    """
    SugarCompose provides the docker compose commands.

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

    def __init__(
        self,
        args: dict[str, str],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
    ):
        """Initialize SugarCompose instance."""
        super().__init__(args, options_args=options_args, cmd_args=cmd_args)

    # container commands
    def _cmd_attach(self) -> None:
        service_name = self.args.get('service', '')
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('attach', services=service_name_list)

    def _cmd_build(self) -> None:
        self._call_backend_app('build', services=self.service_names)

    def _cmd_config(self) -> None:
        self._call_backend_app('config', services=self.service_names)

    def _cmd_cp(self) -> None:
        self._call_backend_app('cp', services=[])

    def _cmd_create(self) -> None:
        self._call_backend_app('create', services=self.service_names)

    def _cmd_down(self) -> None:
        if self.args.get('all') or self.args.get('services'):
            SugarLogs.raise_error(
                "The `down` sub-command doesn't accept `--all` "
                'neither `--services` parameters.',
                SugarErrorType.SUGAR_INVALID_PARAMETER,
            )

        self._call_backend_app(
            'down',
            '--remove-orphans',
            services=[],
        )

    def _cmd_events(self) -> None:
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list = [service_name] if service_name else []
        self._call_backend_app('events', services=service_name_list)

    def _cmd_exec(self) -> None:
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )

        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('exec', services=service_name_list)

    def _cmd_images(self) -> None:
        self._call_backend_app('images', services=self.service_names)

    def _cmd_kill(self) -> None:
        self._call_backend_app('kill', services=self.service_names)

    def _cmd_logs(self) -> None:
        self._call_backend_app('logs', services=self.service_names)

    def _cmd_ls(self) -> None:
        self._call_backend_app('ls', services=[])

    def _cmd_pause(self) -> None:
        self._call_backend_app('pause', services=self.service_names)

    def _cmd_port(self) -> None:
        # port is not complete supported
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`exec` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        # TODO: check how private port could be passed
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('port', services=service_name_list)

    def _cmd_ps(self) -> None:
        self._call_backend_app('ps', services=self.service_names)

    def _cmd_pull(self) -> None:
        self._call_backend_app('pull', services=self.service_names)

    def _cmd_push(self) -> None:
        self._call_backend_app('push', services=self.service_names)

    def _cmd_restart(self) -> None:
        self._call_backend_app('restart', services=self.service_names)

    def _cmd_rm(self) -> None:
        self._call_backend_app('rm', services=self.service_names)

    def _cmd_run(self) -> None:
        service_name = self.args.get('service', '')
        if not service_name:
            SugarLogs.raise_error(
                '`run` sub-command expected --service parameter.',
                SugarErrorType.SUGAR_MISSING_PARAMETER,
            )
        service_name_list: list[str] = [service_name] if service_name else []
        self._call_backend_app('run', services=service_name_list)

    def _cmd_scale(self) -> None:
        self._call_backend_app('ls', services=[])

    def _cmd_start(self) -> None:
        self._call_backend_app('start', services=self.service_names)

    def _cmd_stop(self) -> None:
        self._call_backend_app('stop', services=self.service_names)

    def _cmd_top(self) -> None:
        self._call_backend_app('top', services=self.service_names)

    def _cmd_unpause(self) -> None:
        self._call_backend_app('unpause', services=self.service_names)

    def _cmd_up(self) -> None:
        self._call_backend_app('up', services=self.service_names)

    def _cmd_wait(self) -> None:
        self._call_backend_app('wait', services=self.service_names)

    def _cmd_watch(self) -> None:
        self._call_backend_app('watch', services=self.service_names)
