"""Logs classes and function for sugar system."""

from __future__ import annotations

import os

from enum import Enum

from colorama import Fore


class SugarError(Enum):
    """SugarError group all error types handled by the system."""

    SH_ERROR_RETURN_CODE = 1
    SH_KEYBOARD_INTERRUPT = 2
    SUGAR_CONFIG_FILE_NOT_FOUND = 3
    SUGAR_COMPOSE_APP_NOT_SUPPORTED = 4
    SUGAR_COMPOSE_APP_NOT_FOUNDED = 5
    SUGAR_INVALID_PARAMETER = 6
    SUGAR_MISSING_PARAMETER = 7
    SUGAR_INVALID_CONFIGURATION = 8
    SUGAR_ACTION_NOT_IMPLEMENTED = 9
    SUGAR_NO_SERVICES_RUNNING = 10
    CONFIG_VALIDATION_ERROR = 11
    YAML_PARSING_ERROR = 12
    JSON_SCHEMA_DECODING_ERROR = 13
    CONFIG_VALIDATION_UNEXPECTED_ERROR = 14
    SUGAR_COMMAND_NOT_FOUND = 15
    SUGAR_COMMAND_ERROR = 15
    SUGAR_SWARM_NOT_INITIALIZED = 16
    SUGAR_SWARM_STACK_NAME_NEEDED = 17
    SUGAR_SWARM_STACK_ALREADY_EXISTS = 18
    SUGAR_SWARM_SERVICE_NOT_FOUND = 19


class SugarLogs:
    """SugarLogs is responsible for handling system messages."""

    @staticmethod
    def raise_error(
        message: str,
        message_type: SugarError = SugarError.SH_ERROR_RETURN_CODE,
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
