"""Sugar class for containers."""

from __future__ import annotations

import os

from typing import Dict, Optional, Type, cast

from sugar import __version__
from sugar.logs import KxgrErrorType, KxgrLogs
from sugar.plugins.base import SugarBase, SugarDockerCompose
from sugar.plugins.ext import SugarExt

try:
    from sugar.plugins.stats import SugarStats
except ImportError:
    # SugarStats is optional (extras=tui)
    SugarStats = cast(Optional[Type[SugarBase]], None)  # type: ignore


class Sugar(SugarBase):
    """Sugar main class."""

    plugins_definition: Dict[str, Type[SugarBase]] = {
        'main': SugarDockerCompose,
        'ext': SugarExt,
        **{'stats': SugarStats for i in range(1) if SugarStats is not None},
    }
    plugin: Optional[SugarBase] = None

    def __init__(
        self,
        args: dict,
        options_args: list = [],
        cmd_args: list = [],
    ):
        """Initialize the Sugar object according to the plugin used."""
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

            KxgrLogs.raise_error(
                f'`plugin` parameter `{ self.args.get("plugin") }` '
                f'not found. Options: { plugins_name }.',
                KxgrErrorType.KXGR_INVALID_PARAMETER,
            )
            os._exit(1)

    def get_actions(self) -> list:
        """Get a list of the available actions."""
        actions = []

        for k, v in self.plugins_definition.items():
            actions.extend(v.actions)

        return actions

    def _load_compose_args(self):
        pass

    def _load_service_names(self):
        pass

    def run(self):
        """Run sugar command."""
        if not self.args.get('action'):
            return

        return self.plugin.run()

    # actions available

    def _version(self):
        KxgrLogs.print_info('sugar version:' + str(__version__))
        KxgrLogs.print_info('container program path: ' + str(self.compose_app))
        self._call_compose_app('--version')
