"""Logging utility for i3save - provides verbosity-aware output."""

import sys
from enum import IntEnum


class Verbosity(IntEnum):
    """Verbosity levels for logging output."""

    QUIET = 0  # Only errors
    NORMAL = 1  # Info and errors
    VERBOSE = 2  # All messages (debug, info, errors)


class Logger:
    """A simple logger that respects verbosity levels.

    Provides three output methods that filter based on verbosity:
    - error(): Always shown (QUIET, NORMAL, VERBOSE)
    - info(): Shown at NORMAL and VERBOSE levels
    - debug(): Only shown at VERBOSE level

    Attributes:
        verbosity: The current verbosity level
    """

    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL):
        """Initialize the logger with a verbosity level.

        Args:
            verbosity: The verbosity level to use
        """
        self.verbosity = verbosity

    @classmethod
    def from_flags(cls, quiet: bool = False, verbose: bool = False) -> "Logger":
        """Create a Logger from quiet/verbose boolean flags.

        This is a convenience factory method for creating a logger from
        the CLI flags.

        Args:
            quiet: If True, use QUIET verbosity
            verbose: If True, use VERBOSE verbosity

        Returns:
            A Logger instance with the appropriate verbosity level
        """
        if quiet:
            return cls(Verbosity.QUIET)
        elif verbose:
            return cls(Verbosity.VERBOSE)
        else:
            return cls(Verbosity.NORMAL)

    def error(self, msg: str) -> None:
        """Output an error message.

        Always shown regardless of verbosity level.
        Output goes to stderr.

        Args:
            msg: The error message to display
        """
        print(f"Error: {msg}", file=sys.stderr)

    def info(self, msg: str) -> None:
        """Output an informational message.

        Shown at NORMAL and VERBOSE verbosity levels.

        Args:
            msg: The info message to display
        """
        if self.verbosity >= Verbosity.NORMAL:
            print(msg)

    def debug(self, msg: str) -> None:
        """Output a debug message.

        Only shown at VERBOSE verbosity level.

        Args:
            msg: The debug message to display
        """
        if self.verbosity >= Verbosity.VERBOSE:
            print(msg)
