"""Logs classes and function for sugar system."""

from __future__ import annotations

import os

from enum import Enum

from colorama import Fore


class SugarErrorType(Enum):
    """SugarErrorType group all error types handled by the system."""

    SH_ERROR_RETURN_CODE = 1
    SH_KEYBOARD_INTERRUPT = 2
    SUGAR_COMPOSE_APP_NOT_SUPPORTED = 3
    SUGAR_COMPOSE_APP_NOT_FOUNDED = 4
    SUGAR_INVALID_PARAMETER = 5
    SUGAR_MISSING_PARAMETER = 6
    SUGAR_INVALID_CONFIGURATION = 7
    SUGAR_ACTION_NOT_IMPLEMENTED = 8
    SUGAR_NO_SERVICES_RUNNING = 9


class SugarLogs:
    """SugarLogs is responsible for handling system messages."""

    @staticmethod
    def raise_error(
        message: str,
        message_type: SugarErrorType = SugarErrorType.SH_ERROR_RETURN_CODE,
    ) -> None:
        """Print error message and exit with given error code."""
        print(Fore.RED, f'[EE] {message}', Fore.RESET)
        os._exit(message_type.value)

    @staticmethod
    def print_info(message: str) -> None:
        """Print info message."""
        print(Fore.BLUE, message, Fore.RESET)

    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message."""
        print(Fore.YELLOW, message, Fore.RESET)
