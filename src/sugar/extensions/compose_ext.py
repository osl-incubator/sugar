"""SugarComposeExt Plugin class for containers."""

from __future__ import annotations

from sugar.docs import docparams
from sugar.extensions.compose import (
    SugarCompose,
    doc_common_services,
)


class SugarComposeExt(SugarCompose):
    """SugarComposeExt provides extra commands on top of docker-compose."""

    @docparams(doc_common_services)
    def _cmd_restart(
        self,
        group: str,
        services: str,
        all: bool,
        options: str,
        config_file: str,
        verbose: bool,
    ) -> None:
        """Restart services (compose stop + up)."""
        options = self.options_args
        self.options_args = []
        self._cmd_stop()
        self.options_args = options
        self._cmd_start()

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        group: str,
        services: str,
        all: bool,
        options: str,
        config_file: str,
        verbose: bool,
    ) -> None:
        """Start services (compose up)."""
        self._cmd_up()
