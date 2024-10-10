"""SugarComposeExt Plugin class for containers."""

from __future__ import annotations

from sugar.extensions.compose import SugarCompose
from sugar.logs import SugarErrorType, SugarLogs


class SugarComposeExt(SugarCompose):
    """SugarComposeExt provides extra commands on top of docker-compose."""

    def __init__(
        self,
        args: dict[str, str],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
    ) -> None:
        """Initialize the SugarComposeExt class."""
        super().__init__(args, options_args=options_args, cmd_args=cmd_args)

    def _cmd_get_ip(self) -> None:
        SugarLogs.raise_error(
            '`get-ip` mot implemented yet.',
            SugarErrorType.SUGAR_ACTION_NOT_IMPLEMENTED,
        )

    def _cmd_restart(self) -> None:
        options = self.options_args
        self.options_args = []
        self._cmd_stop()
        self.options_args = options
        self._cmd_start()

    def _cmd_start(self) -> None:
        self._cmd_up()

    def _cmd_wait(self) -> None:
        SugarLogs.raise_error(
            '`wait` not implemented yet.',
            SugarErrorType.SUGAR_ACTION_NOT_IMPLEMENTED,
        )
