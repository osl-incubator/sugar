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
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Restart services (compose stop + up)."""
        self._cmd_stop(services=services, all=all)
        self._cmd_start(services=services, all=all, options=options)

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services (compose up)."""
        self._cmd_up(services=services, all=all, options=options)
