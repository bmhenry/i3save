"""Custom exceptions for i3save."""


class I3SaveError(Exception):
    """Base exception for all i3save errors."""

    pass


class I3NotRunningError(I3SaveError):
    """Raised when i3 is not running or IPC connection fails."""

    pass


class I3MsgNotFoundError(I3SaveError):
    """Raised when i3-msg is not found in PATH."""

    pass


class I3CommandError(I3SaveError):
    """Raised when an i3-msg command fails."""

    pass


class ConfigFileError(I3SaveError):
    """Raised for file read/write/parse errors."""

    pass
