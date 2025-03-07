"""Helper functions for documentation."""

from __future__ import annotations

import functools
import inspect

from inspect import _ParameterKind
from typing import Any, Callable, Dict, Protocol, TypeVar, Union, cast

from typing_extensions import TypeAlias

F = TypeVar('F', bound=Callable[..., Any])

MetaDocsParams: TypeAlias = Dict[str, Dict[str, str]]
MetaDocs: TypeAlias = Dict[str, Union[str, MetaDocsParams]]


class DecoratedMetaDocsFunction(Protocol):
    """Type for functions with _meta_docs."""

    _meta_docs: MetaDocs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Define a placeholder for the type."""
        ...


def docparams(
    param_docs: Dict[str, str],
) -> Callable[[F], DecoratedMetaDocsFunction]:
    """
    Decorate functions to add dynamic parameters to docs and metadata.

    Decorator to update the function's docstring with parameter documentation
    and add a '_meta_docs' attribute containing parameter details.

    Parameters
    ----------
    param_docs : Dict[str, str]
        A dictionary mapping parameter names to their docstring descriptions.

    Returns
    -------
    Callable
        The decorated function with updated docstring and '_meta_docs'.
    """

    def decorator(func: F) -> DecoratedMetaDocsFunction:  # noqa: PLR0912
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        sig = inspect.signature(func)
        annotations = func.__annotations__

        # Build the _meta_docs dictionary
        parameters: MetaDocsParams = {}

        for name, param in sig.parameters.items():
            if name == 'self':
                continue
            param_info = {}
            if name in annotations:
                param_type = annotations[name]
                if isinstance(param_type, type):
                    param_info['type'] = param_type.__name__
                else:
                    param_info['type'] = str(param_type)
            if name in param_docs:
                param_info['help'] = param_docs[name]
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default

            param_info['positional_only'] = repr(
                param.kind == _ParameterKind.POSITIONAL_ONLY
            )

            parameters[name] = param_info

        # Build parameter documentation
        param_docs_lines = []
        for name, info in parameters.items():
            param_line = f'{name} : {info.get("type", "")}'
            param_docs_lines.append(param_line)
            default = info.get('default', None)
            if default is not None:
                param_docs_lines.append(f'    Default: {default}')
            docstring = info.get('help', '')
            if docstring:
                param_docs_lines.append(f'    {docstring}')
            param_docs_lines.append('')  # Empty line for separation

        # Update the function's docstring
        doc = func.__doc__ or ''
        # Split the docstring into lines
        doc_lines = doc.strip().split('\n')
        # Find the 'Parameters' section
        params_index = None
        for i, line in enumerate(doc_lines):
            if line.strip().lower() in ('parameters:', 'parameters'):
                params_index = i
                break
        if params_index is not None:
            # Remove existing parameter documentation
            next_section_index = None
            for j in range(params_index + 1, len(doc_lines)):
                if doc_lines[j].strip() == '':
                    continue
                elif doc_lines[j].startswith(' '):
                    continue  # Indented parameter documentation
                elif doc_lines[j].endswith(':') and not doc_lines[
                    j
                ].startswith(' '):
                    next_section_index = j
                    break
            if next_section_index is None:
                next_section_index = len(doc_lines)
            doc_lines = (
                doc_lines[: params_index + 1] + doc_lines[next_section_index:]
            )
            doc_lines.insert(params_index + 1, '')
            doc_lines[params_index + 2 : params_index + 2] = param_docs_lines
        else:
            # Append 'Parameters' section at the end
            if doc_lines and doc_lines[-1].strip() != '':
                doc_lines.append('')
            doc_lines.append('Parameters:')
            doc_lines.append('-----------')
            doc_lines.append('')
            doc_lines.extend(param_docs_lines)

        # Reconstruct the docstring
        updated_doc = '\n'.join(doc_lines)
        wrapper.__doc__ = updated_doc

        meta_docs: MetaDocs = {
            'title': func.__doc__ or '',
            'parameters': parameters,
        }

        # Set the _meta_docs attribute
        setattr(wrapper, '_meta_docs', meta_docs)

        return cast(DecoratedMetaDocsFunction, wrapper)

    return decorator
