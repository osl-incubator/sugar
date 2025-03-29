"""TUI extension for Sugar."""

from __future__ import annotations

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarLogs


class SugarTUI(SugarBase):
    """Terminal User Interface extension for Sugar."""

    def _load_backend(self) -> None:
        """Load backend and backend parameters."""
        pass

    @docparams({})  # Empty dict since we don't have parameters
    def _cmd_tui(self) -> None:
        """Launch the Sugar Terminal User Interface."""
        SugarLogs.print_info('Starting Sugar TUI...')
        try:
            from sugar.tui.app import run

            SugarLogs.print_info('Successfully imported run function')
            run()
            SugarLogs.print_info(
                'TUI has completed'
            )  # This will only print if run() completes/exits
        except Exception as e:
            SugarLogs.print_warning(f'Error launching TUI: {e}')
            import traceback

            traceback.print_exc()
