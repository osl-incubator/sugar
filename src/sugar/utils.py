"""General utilities functions."""

import re


def camel_to_snake(name: str, sep: str = '-') -> str:
    """
    Convert camelCase or PascalCase string to snake_case.

    Parameters
    ----------
    name : str
        The string to convert.

    Returns
    -------
    str
        The converted snake_case string.
    """
    # Add underscore between lowercase and uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1' + sep + r'\2', name)
    # Add underscore before a sequence of uppercase letters
    snake_case = re.sub('([a-z0-9])([A-Z])', r'\1' + sep + r'\2', s1).lower()
    return snake_case


# prepend stack name to the services list and stack is should be provided
# if not throw error
def prepend_stack_name(stack_name: str, services: list[str]) -> list[str]:
    """
    Prepend stack name to the services list.

    Parameters
    ----------
    stack_name : str
        The name of the stack.

    services : list[str]
        The list of services.

    Returns
    -------
    list[str]
        The list of services with the stack name prepended.
    """
    if not stack_name:
        raise ValueError('Stack name is needed')
    return [f'{stack_name}_{service}' for service in services]
