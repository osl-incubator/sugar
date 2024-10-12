"""Sugar class for containers."""

from __future__ import annotations

from typing import Optional, Type, cast

from sugar.extensions.base import SugarBase
from sugar.extensions.compose import SugarCompose
from sugar.extensions.compose_ext import SugarComposeExt

try:
    from sugar.extensions.stats import SugarStats
except ImportError:
    # SugarStats is optional (extras=tui)
    SugarStats = cast(Optional[Type[SugarBase]], None)  # type: ignore


extensions: dict[str, Type[SugarBase]] = {
    'compose': SugarCompose,
    'compose-ext': SugarComposeExt,
    **{'stats': SugarStats for i in range(1) if SugarStats is not None},
}
