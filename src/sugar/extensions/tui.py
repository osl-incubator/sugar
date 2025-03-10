"""TUI extension for Sugar."""

from __future__ import annotations

from sugar.docs import docparams
from sugar.extensions.base import SugarBase


class TUIExtension(SugarBase):
    """Terminal User Interface extension for Sugar."""

    # Notice there's no 'actions' property defined here - it's handled by the base class

    @docparams({})  # Empty dict since we don't have parameters
    def _cmd_tui(self) -> None:
     """Launch the Sugar Terminal User Interface."""
    print("Starting Sugar TUI...")
    try:
        from sugar.tui.app import run
        print("Successfully imported run function")
        run()
        print("TUI has completed") # This will only print if run() completes/exits
    except Exception as e:
        print(f"Error launching TUI: {e}")
        import traceback
        traceback.print_exc()