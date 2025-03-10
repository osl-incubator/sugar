"""Functions about console."""

from __future__ import annotations

import os


def get_terminal_size() -> tuple[int, int]:
    """Return the width and height of the terminal using os module."""
    try:
        size = os.get_terminal_size()
        width = size.columns
        height = size.lines
    except OSError:
        # Default values if the terminal size cannot be determined.
        width = 80
        height = 24

    return width, height
