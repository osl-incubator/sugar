"""Logs classes and function for sugar system."""
import os

from enum import Enum

from colorama import Fore


class KxgrErrorType(Enum):
    """KxgrErrorType group all error types handled by the system."""

    SH_ERROR_RETURN_CODE = 1
    SH_KEYBOARD_INTERRUPT = 2
    KXGR_COMPOSE_APP_NOT_SUPPORTED = 3
    KXGR_COMPOSE_APP_NOT_FOUNDED = 4
    KXGR_INVALID_PARAMETER = 5
    KXGR_MISSING_PARAMETER = 6
    KXGR_INVALID_CONFIGURATION = 7
    KXGR_ACTION_NOT_IMPLEMENTED = 8


class KxgrLogs:
    """KxgrLogs is responsible for handling system messages."""

    @staticmethod
    def raise_error(message: str, message_type: KxgrErrorType):
        """Print error message and exit with given error code."""
        print(Fore.RED, f'[EE] {message}', Fore.RESET)
        os._exit(message_type.value)

    @staticmethod
    def print_info(message: str):
        """Print info message."""
        print(Fore.BLUE, message, Fore.RESET)

    @staticmethod
    def print_warning(message: str):
        """Print warning message."""
        print(Fore.YELLOW, message, Fore.RESET)
