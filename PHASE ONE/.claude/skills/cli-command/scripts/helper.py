#!/usr/bin/env python3
"""CLI Command Helper - Generate CLI command boilerplate code."""

import sys
from pathlib import Path

CLI_COMMAND_TEMPLATE = """
@app.command("{cmd_name}")
def {func_name}(
    {arg_name}: {arg_type} = typer.Argument(..., help="{arg_help}"),
    {opt_name}: Optional[{opt_type}] = typer.Option(
        None,
        "--{opt_flag}",
        help="{opt_help}"
    ),
) -> None:
    '''
    {cmd_description}

    Examples:

      Basic usage:
      $ todo {cmd_name} {example_basic}

      With options:
      $ todo {cmd_name} {example_with_opts}
    '''
    try:
        # Validate inputs
        # TODO: Add validation logic

        # Call service layer
        # result = service.{func_name}({arg_name})

        # Format output with rich
        console.print("[green][/green] Operation successful")

    except ValidationError as e:
        console.print(f"[red]Error:[/red] {{e}}")
        console.print("[yellow]Hint:[/yellow] Check input format")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {{e}}")
        raise typer.Exit(code=2)
"""

def generate_command(
    name: str,
    description: str,
    arg_name: str = "value",
    arg_type: str = "str"
) -> str:
    """
    Generate CLI command boilerplate.

    Args:
        name: Command name (e.g., "search", "filter")
        description: Command description for docstring
        arg_name: Argument parameter name
        arg_type: Argument type hint

    Returns:
        Generated command code
    """
    func_name = name.replace("-", "_")

    return CLI_COMMAND_TEMPLATE.format(
        cmd_name=name,
        func_name=func_name,
        arg_name=arg_name,
        arg_type=arg_type,
        arg_help=f"{arg_name.capitalize()} to process",
        opt_name="force",
        opt_type="bool",
        opt_flag="force",
        opt_help="Skip confirmation prompts",
        cmd_description=description,
        example_basic=f"<{arg_name}>",
        example_with_opts=f"<{arg_name}> --force"
    )


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("CLI Command Helper")
        print("\nUsage:")
        print("  helper.py <command-name> <description>")
        print("\nExample:")
        print("  helper.py search 'Search tasks by keyword'")
        print("\nOutput: Generated command code to stdout")
        sys.exit(1)

    cmd_name = sys.argv[1]
    description = sys.argv[2]

    code = generate_command(cmd_name, description)
    print(code)


if __name__ == "__main__":
    main()
