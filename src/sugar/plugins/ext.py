"""SugarExt Plugin class for containers."""

from __future__ import annotations

from typing import Any

from sugar.logs import SugarErrorType, SugarLogs
from sugar.plugins.base import SugarDockerCompose


class SugarExt(SugarDockerCompose):
    """SugarExt provides special commands not available on docker-compose."""

    def __init__(self, args: dict[str, str], **kwargs: Any) -> None:
        """Initialize the SugarExt class."""
        self.actions += [
            'get-ip',
            'restart',
            'start',
            'stop',
            'wait',
        ]

        super().__init__(args, **kwargs)

    def _get_ip(self) -> None:
        SugarLogs.raise_error(
            '`get-ip` mot implemented yet.',
            SugarErrorType.SUGAR_ACTION_NOT_IMPLEMENTED,
        )

    def _restart(self) -> None:
        options = self.options_args
        self.options_args = []
        self._stop()
        self.options_args = options
        self._start()

    def _start(self) -> None:
        self._up()

    def _wait(self) -> None:
        SugarLogs.raise_error(
            '`wait` not implemented yet.',
            SugarErrorType.SUGAR_ACTION_NOT_IMPLEMENTED,
        )
