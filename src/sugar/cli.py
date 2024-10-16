"""Definition of the CLI structure."""

from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, Union, cast

import click
import typer

from typer import Option

from sugar import __version__
from sugar.core import extensions
from sugar.docs import MetaDocs, MetaDocsParams
from sugar.logs import SugarLogs

# "count" means the number of parameters expected for each flag
CLI_ROOT_FLAGS_VALUES_COUNT = {
    '--dry-run': 0,
    '--file': 1,
    '--group': 1,
    '--help': 0,  # not necessary to store this value
    '--verbose': 0,
    '--version': 0,  # not necessary to store this value
}

flags_state: dict[str, bool] = {
    'verbose': False,
}

flags_group: dict[str, str] = {
    'group': '',
}

flags_dry_run: dict[str, bool] = {
    'dry_run': False,
}

opt_state: dict[str, list[Any]] = {
    'options': [],
    'cmd': [],
}

sugar_exts = {
    ext_name: ext_class() for ext_name, ext_class in extensions.items()
}

typer_groups: dict[str, typer.Typer] = {}

app = typer.Typer(
    name='sugar',
    help=(
        'Sugar is a tool that help you to organize'
        "and simplify your containers' stack."
    ),
    epilog=(
        'If you have any problem, open an issue at: '
        'https://github.com/osl-incubator/sugar'
    ),
    short_help="Sugar is a tool that help you \
        to organize containers' stack",
)


def _check_sugar_file(file_path: str = '.sugar.yaml') -> bool:
    return Path(file_path).exists()


def version_callback() -> None:
    """Print the Sugar version."""
    SugarLogs.print_info(f'Sugar version: {__version__}')


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: str = Option(
        '',
        '--file',
        help='Set the sugar config file.',
    ),
    group: str = Option(
        '',
        '--group',
        help='Set the group of services for running the sugar command.',
    ),
    version: bool = Option(
        None,
        '--version',
        '-v',
        is_flag=True,
        is_eager=True,
        help='Show the version of sugar.',
    ),
    verbose: bool = Option(
        False,
        '--verbose',
        is_flag=True,
        is_eager=True,
        help='Show the command executed.',
    ),
    dry_run: bool = Option(
        False,
        '--dry-run',
        is_flag=True,
        is_eager=True,
        help="Don't actually execute the command.",
    ),
) -> None:
    """
    Process commands for specific flags.

    Otherwise, show the help menu.
    """
    ctx.ensure_object(dict)

    if verbose:
        # global
        flags_state['verbose'] = True

    if group:
        # global
        flags_group['group'] = group

    if dry_run:
        # global
        flags_dry_run['dry_run'] = True

    if ctx.invoked_subcommand is None:
        raise typer.Exit()


def map_type_from_string(type_name: str) -> Type[Union[str, int, float, bool]]:
    """
    Return a type object mapped from the type name.

    Parameters
    ----------
    type_name : str
        The string representation of the type.

    Returns
    -------
    type
        The corresponding Python type.
    """
    type_mapping = {
        'str': str,
        'string': str,
        'int': int,
        'integer': int,
        'float': float,
        'bool': bool,
        'boolean': bool,
    }
    return type_mapping.get(type_name, str)


def normalize_string_type(type_name: str) -> str:
    """
    Normalize the user type definition to the correct name.

    Parameters
    ----------
    type_name : str
        The string representation of the type.

    Returns
    -------
    str
        The corresponding makim type name.
    """
    type_mapping = {
        'str': 'str',
        'string': 'str',
        'int': 'int',
        'integer': 'int',
        'float': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        # Add more mappings as needed
    }
    return type_mapping.get(type_name, 'str')


def get_default_value(
    arg_type: str, value: Any
) -> Optional[Union[str, int, float, bool]]:
    """Return the default value regarding its type in a string format."""
    if arg_type == 'bool':
        return False if value is None else bool(value)
    elif arg_type == 'int':
        return int(value) if value is not None else None
    elif arg_type == 'float':
        return float(value) if value is not None else None
    elif arg_type == 'str':
        return str(value) if value is not None else None
    return None


def get_default_value_str(arg_type: str, value: Any) -> str:
    """Return the default value regarding its type in a string format."""
    if arg_type == 'str':
        return f'"{value}"'

    if arg_type == 'bool':
        return 'False'

    return f'{value or 0}'


def create_args_string(args: dict[str, dict[str, str]]) -> str:
    """Return a string for arguments for a function for typer."""
    args_rendered = []

    arg_template = (
        '{arg_name}: Optional[{arg_type}] = typer.Option('
        '{default_value}, '
        '"--{name_flag}", '
        'help="{help_text}"'
        ')'
    )

    for name, spec in args.items():
        name_clean = name.replace('-', '_')
        arg_type = normalize_string_type(spec.get('type', 'str'))
        help_text = spec.get('help', '')
        default_value = 'None'

        if not spec.get('required', False) and not spec.get(
            'interactive', False
        ):
            default_value = spec.get('default', '')
            default_value = get_default_value_str(arg_type, default_value)

        arg_str = arg_template.format(
            **{
                'arg_name': name_clean,
                'arg_type': arg_type,
                'default_value': default_value,
                'name_flag': name,
                'help_text': help_text.replace('\n', '\\n'),
            }
        )

        args_rendered.append(arg_str)

    return ', '.join(args_rendered)


def apply_click_options(
    command_function: Callable[..., Any], options: dict[str, Any]
) -> Callable[..., Any]:
    """
    Apply Click options to a Typer command function.

    Parameters
    ----------
    command_function : callable
        The Typer command function to which options will be applied.
    options : dict
        A dictionary of options to apply.

    Returns
    -------
    callable
        The command function with options applied.
    """
    for opt_name, opt_details in options.items():
        opt_args: dict[
            str, Optional[Union[str, int, float, bool, Type[Any]]]
        ] = {}

        opt_data = cast(Dict[str, str], opt_details)
        opt_type_str = normalize_string_type(opt_data.get('type', 'str'))
        opt_default = get_default_value(opt_type_str, opt_data.get('default'))

        if opt_type_str == 'bool':
            opt_args.update({'is_flag': True})

        opt_args.update(
            {
                'default': None
                if opt_data.get('interactive', False)
                else opt_default,
                'type': map_type_from_string(opt_type_str),
                'help': opt_data.get('help', ''),
                'show_default': True,
            }
        )

        click_option = click.option(
            f'--{opt_name}',
            **opt_args,  # type: ignore[arg-type]
        )
        command_function = click_option(command_function)

    return command_function


def create_dynamic_command(
    ext_name: str,
    typer_group: typer.Typer,
    meta: MetaDocs,
) -> None:
    """
    Dynamically create a Typer command with the specified options.

    Parameters
    ----------
    typer_group : typer.Typer
    name : str
        The command name.
    meta : dict
        the action/command metadata
    """
    name = cast(str, meta.get('name', ''))
    args = cast(Dict[str, Dict[str, str]], meta.get('parameters', {}))
    fn_help = cast(str, meta.get('title', ''))

    args_str = create_args_string(args)
    args_param_list: list[str] = []

    for arg, arg_details in args.items():
        arg_clean = arg.replace('-', '_')
        args_param_list.append(f'{arg}={arg_clean}')

    args_param_str = ','.join(args_param_list)

    decorator = typer_group.command(
        name,
        help=fn_help,
    )

    function_code = f'def dynamic_command({args_str}):\n'

    # handle interactive prompts
    for arg, arg_details in args.items():
        arg_clean = arg.replace('-', '_')

    function_code += f'    sugar = sugar_exts.get("{ext_name}")\n'
    function_code += f'    sugar._cmd_{name}({args_param_str})\n'

    local_vars: dict[str, Any] = {}
    exec(function_code, globals(), local_vars)
    dynamic_command = decorator(local_vars['dynamic_command'])

    # Apply Click options to the Typer command
    if 'args' in args:
        options_data = cast(Dict[str, Dict[str, Any]], args.get('args', {}))
        dynamic_command = apply_click_options(dynamic_command, options_data)


def extract_options_and_cmd_args() -> tuple[list[str], list[str]]:
    """Extract arg `options` and `cmd` from the CLI calling."""
    args = list(sys.argv)
    total_args = len(args)

    if '--options' in args:
        options_sep_idx = args.index('--options')
    else:
        options_sep_idx = None

    if '--cmd' in args:
        cmd_sep_idx = args.index('--cmd')
    else:
        cmd_sep_idx = None

    if options_sep_idx is None and cmd_sep_idx is None:
        return [], []

    # check if --options or --cmd are the last ones in the command line
    first_sep_idx = min(
        [(options_sep_idx or total_args), (cmd_sep_idx or total_args)]
    )
    for sugar_arg in [
        '--verbose',
        '--version',
        '--group',
        '--services',
        '--service',
        '--all',
        '--file',
    ]:
        if sugar_arg not in args:
            continue

        if first_sep_idx < args.index(sugar_arg):
            print(
                '[EE] The parameters --options/--cmd should be the '
                'last ones in the command line.'
            )
            os._exit(1)

    for ind in range(first_sep_idx, total_args):
        sys.argv.pop(first_sep_idx)

    options_sep_idx = options_sep_idx or total_args
    cmd_sep_idx = cmd_sep_idx or total_args

    if options_sep_idx < cmd_sep_idx:
        options_args = args[options_sep_idx + 1 : cmd_sep_idx]
        cmd_args = args[cmd_sep_idx + 1 :]
    else:
        cmd_args = args[cmd_sep_idx + 1 : options_sep_idx]
        options_args = args[options_sep_idx + 1 :]
    return options_args, cmd_args


def extract_root_config(
    cli_list: list[str] = sys.argv,
) -> dict[str, str | bool]:
    """Extract the root configuration from the CLI."""
    params = cli_list[1:]

    # default values
    sugar_file = '.sugar.yaml'
    group = ''
    dry_run = False
    verbose = False

    try:
        idx = 0
        while idx < len(params):
            arg = params[idx]
            if arg not in CLI_ROOT_FLAGS_VALUES_COUNT:
                break

            if arg == '--file':
                try:
                    sugar_file = params[idx + 1]
                except IndexError:
                    pass
            elif arg == '--group':
                try:
                    group = params[idx + 1]
                except IndexError:
                    pass
            elif arg == '--dry-run':
                dry_run = True
            elif arg == '--verbose':
                verbose = True

            idx += 1 + CLI_ROOT_FLAGS_VALUES_COUNT[arg]
    except Exception:
        red_text = typer.style(
            'The sugar config file was not correctly detected. '
            'Using the default .sugar.yaml.',
            fg=typer.colors.RED,
            bold=True,
        )
        typer.echo(red_text, err=True, color=True)

    return {
        'file': sugar_file,
        'group': group,
        'dry_run': dry_run,
        'verbose': verbose,
    }


def _get_command_from_cli() -> str:
    """
    Get the group and task from CLI.

    This function is based on `CLI_ROOT_FLAGS_VALUES_COUNT`.
    """
    params = sys.argv[1:]
    command = ''

    try:
        idx = 0
        while idx < len(params):
            arg = params[idx]
            if arg not in CLI_ROOT_FLAGS_VALUES_COUNT:
                command = f'flag `{arg}`' if arg.startswith('--') else arg
                break

            idx += 1 + CLI_ROOT_FLAGS_VALUES_COUNT[arg]
    except Exception as e:
        print(e)

    return command


def run_app() -> None:
    """Run the typer app."""
    root_config = extract_root_config()

    config_file_path = cast(str, root_config.get('file', '.sugar.yaml'))

    cli_completion_words = [
        w for w in os.getenv('COMP_WORDS', '').split('\n') if w
    ]

    if not _check_sugar_file(config_file_path) and cli_completion_words:
        # autocomplete call
        root_config = extract_root_config(cli_completion_words)
        config_file_path = cast(str, root_config.get('file', '.sugar.yaml'))
        if not _check_sugar_file(config_file_path):
            return

    for sugar_ext in sugar_exts.values():
        sugar_ext.load(
            file=config_file_path,
            group=cast(str, root_config.get('group', '')),
            dry_run=cast(bool, root_config.get('dry_run', False)),
            verbose=cast(bool, root_config.get('verbose', False)),
        )

    commands: dict[str, list[MetaDocs]] = {}
    actions: list[str] = []

    for ext_name, ext_class in extensions.items():
        ext_obj = ext_class()
        commands[ext_name] = []

        actions = ext_obj.actions

        for action in actions:
            fn_name = f'_cmd_{action}'
            fn = getattr(ext_obj, fn_name)
            title = fn._meta_docs.get('title', '')

            commands[ext_name].append(
                cast(
                    MetaDocs,
                    {
                        'name': action,
                        'title': title,
                        'parameters': cast(
                            MetaDocsParams, fn._meta_docs.get('parameters', {})
                        ),
                    },
                )
            )

    # Add dynamically created commands to Typer app
    for ext_name, actions_meta in commands.items():
        ext_obj = extensions[ext_name]()

        if not ext_obj:
            SugarLogs.raise_error(f'Extension not found ({ext_name}).')

        typer_group = typer.Typer(
            help=ext_obj.__doc__,
            invoke_without_command=True,
        )
        typer_groups[ext_name] = typer_group

        for action_meta in actions_meta:
            create_dynamic_command(ext_name, typer_group, action_meta)

    for ext_name, typer_group in typer_groups.items():
        app.add_typer(typer_group, name=ext_name, rich_help_panel='COMMAND')

    try:
        app()
    except SystemExit as e:
        # code 2 means code not found
        error_code = 2
        if e.code != error_code:
            raise e

        command_used = _get_command_from_cli()
        typer.secho(f'Command {command_used} not found.', fg='red')

        raise e


if __name__ == '__main__':
    run_app()
