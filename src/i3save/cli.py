"""Command-line interface for i3save."""

import argparse
import sys

from . import __version__
from . import save as save_module
from . import restore as restore_module
from .exceptions import (
    ConfigFileError,
    I3CommandError,
    I3MsgNotFoundError,
    I3NotRunningError,
    I3SaveError,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser with save and restore subcommands
    """
    parser = argparse.ArgumentParser(
        prog="i3save",
        description="Save and restore i3 workspace-to-monitor mappings"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # Global verbosity flags (mutually exclusive)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="suppress normal output (only show errors)"
    )
    verbosity.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show detailed output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="available commands"
    )

    # Save subcommand
    save_parser = subparsers.add_parser(
        "save",
        help="save current workspace layout to a file"
    )
    save_parser.add_argument(
        "file",
        help="path to save the workspace mapping"
    )

    # Restore subcommand
    restore_parser = subparsers.add_parser(
        "restore",
        help="restore workspace layout from a file"
    )
    restore_parser.add_argument(
        "file",
        help="path to the saved workspace mapping"
    )

    return parser


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Parses arguments, dispatches to the appropriate command handler,
    and returns an exit code.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:] if None)

    Returns:
        Exit code: 0 for success, non-zero for failure
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Show help if no command provided
    if parsed.command is None:
        parser.print_help()
        return 1

    # Dispatch to appropriate command
    try:
        if parsed.command == "save":
            return save_module.save(
                filepath=parsed.file,
                quiet=parsed.quiet,
                verbose=parsed.verbose
            )
        elif parsed.command == "restore":
            return restore_module.restore(
                filepath=parsed.file,
                quiet=parsed.quiet,
                verbose=parsed.verbose
            )
    except I3MsgNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Make sure i3 is installed and i3-msg is in your PATH.", file=sys.stderr)
        return 2
    except I3NotRunningError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Make sure i3 is running.", file=sys.stderr)
        return 3
    except I3CommandError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 4
    except ConfigFileError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 5
    except I3SaveError as e:
        # Catch any other i3save-specific errors
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Should not reach here
    return 1


if __name__ == "__main__":
    sys.exit(main())
