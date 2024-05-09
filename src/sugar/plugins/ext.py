"""SugarExt Plugin class for containers."""

from __future__ import annotations

from sugar.logs import KxgrErrorType, KxgrLogs
from sugar.plugins.base import SugarDockerCompose


class SugarExt(SugarDockerCompose):
    """SugarExt provides special commands not available on docker-compose."""

    def __init__(self, *args, **kwargs):
        """Initialize the SugarExt class."""
        self.actions += [
            'get-ip',
            'restart',
            'start',
            'stop',
            'wait',
        ]

        super().__init__(*args, **kwargs)

    def _get_ip(self):
        KxgrLogs.raise_error(
            '`get-ip` mot implemented yet.',
            KxgrErrorType.KXGR_ACTION_NOT_IMPLEMENTED,
        )

    def _restart(self):
        options = self.options_args
        self.options_args = []
        self._stop()
        self.options_args = options
        self._start()

    def _start(self):
        self._up()

    def _wait(self):
        KxgrLogs.raise_error(
            '`wait` not implemented yet.',
            KxgrErrorType.KXGR_ACTION_NOT_IMPLEMENTED,
        )
