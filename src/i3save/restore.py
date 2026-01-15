"""Restore functionality for i3save - restores workspace-to-output mappings."""

import json
from pathlib import Path

from . import i3
from .exceptions import ConfigFileError
from .logging import Logger


def load_from_file(filepath: str) -> dict:
    """Load workspace mapping from a JSON file.

    Args:
        filepath: Path to the JSON file containing workspace mappings

    Returns:
        Dictionary with 'focused' and 'workspaces' keys

    Raises:
        ConfigFileError: If the file does not exist or contains invalid JSON
    """
    path = Path(filepath)

    if not path.exists():
        raise ConfigFileError(f"Configuration file not found: {filepath}")

    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigFileError(f"Invalid JSON in configuration file: {e}")
    except OSError as e:
        raise ConfigFileError(f"Failed to read file '{filepath}': {e}")


def get_available_outputs() -> dict[str, dict]:
    """Get dictionary of active outputs/monitors.

    Queries i3 for all outputs and filters to only active ones.

    Returns:
        Dictionary mapping output name to output info including:
        - name: Output name (e.g., 'HDMI-1')
        - rect: Dict with width, height, x, y
        - active: True (only active outputs are included)
    """
    outputs = i3.get_outputs()
    available = {}

    for output in outputs:
        if output.get("active", False):
            available[output["name"]] = output

    return available


def find_largest_output(outputs: dict[str, dict]) -> str:
    """Find the output with the largest resolution.

    Args:
        outputs: Dictionary mapping output name to output info (from get_available_outputs)

    Returns:
        Name of the output with largest resolution (width * height)

    Raises:
        ValueError: If no outputs are available
    """
    if not outputs:
        raise ValueError("No available outputs found")

    # Initialize with first output as default
    largest_name = next(iter(outputs.keys()))
    largest_area = 0

    for name, output in outputs.items():
        rect = output.get("rect", {})
        width = rect.get("width", 0)
        height = rect.get("height", 0)
        area = width * height

        if area > largest_area:
            largest_area = area
            largest_name = name

    return largest_name


def get_current_workspaces() -> set[str]:
    """Get set of currently existing workspace names.

    Returns:
        Set of workspace name strings
    """
    workspaces = i3.get_workspaces()
    return {ws["name"] for ws in workspaces}


def restore_workspaces(mapping: dict, logger: Logger) -> tuple[int, int]:
    """Restore workspaces to their saved output locations.

    Iterates through saved workspaces and moves each to its target output.
    If the target output doesn't exist, falls back to the largest available output.
    Skips workspaces that no longer exist.

    Args:
        mapping: Dictionary with 'workspaces' list containing name/output pairs
        logger: Logger instance for output messages

    Returns:
        Tuple of (successful_count, skipped_count)
    """
    available_outputs = get_available_outputs()
    current_workspaces = get_current_workspaces()
    fallback_output = find_largest_output(available_outputs)

    successful = 0
    skipped = 0

    for ws in mapping.get("workspaces", []):
        ws_name = ws["name"]
        target_output = ws["output"]

        # Check if workspace still exists
        if ws_name not in current_workspaces:
            logger.debug(f"  Workspace '{ws_name}' no longer exists, skipping")
            skipped += 1
            continue

        # Check if target output exists, use fallback if not
        actual_output = target_output
        if target_output not in available_outputs:
            actual_output = fallback_output
            logger.debug(f"  Output '{target_output}' not found, using fallback '{fallback_output}'")

        # Move workspace to output
        success = i3.move_workspace_to_output(ws_name, actual_output)

        if success:
            successful += 1
            logger.debug(f"  Moved workspace '{ws_name}' to output '{actual_output}'")
        else:
            skipped += 1
            logger.info(f"  Failed to move workspace '{ws_name}' to output '{actual_output}'")

    return (successful, skipped)


def restore(filepath: str, quiet: bool = False, verbose: bool = False) -> int:
    """Restore workspace layout from a file.

    Main entry point for the restore command. Loads saved workspace positions
    and restores them, then restores visible workspaces on each output, and
    finally refocuses the previously focused workspace.

    Args:
        filepath: Path to the saved workspace mapping file
        quiet: If True, suppress normal output (only show errors)
        verbose: If True, show detailed output

    Returns:
        Exit code: 0 for success, non-zero for failure

    Raises:
        I3SaveError: If i3 communication or file operations fail
    """
    logger = Logger.from_flags(quiet=quiet, verbose=verbose)

    logger.debug(f"Loading workspace mapping from {filepath}")

    mapping = load_from_file(filepath)

    logger.debug(f"Found {len(mapping.get('workspaces', []))} saved workspace(s)")

    successful, skipped = restore_workspaces(mapping, logger)

    # Restore visible workspaces on each output
    visible_workspaces = mapping.get("visible_workspaces", [])
    if visible_workspaces:
        current_workspaces = get_current_workspaces()
        logger.debug(f"Restoring {len(visible_workspaces)} visible workspace(s)")

        for ws in visible_workspaces:
            ws_name = ws["name"]
            if ws_name in current_workspaces:
                i3.focus_workspace(ws_name)
                logger.debug(f"  Made workspace '{ws_name}' visible on output '{ws['output']}'")
            else:
                logger.debug(f"  Workspace '{ws_name}' no longer exists, skipping visibility restore")

    # Restore focus to the previously focused workspace (do this last to ensure correct focus)
    focused = mapping.get("focused")
    if focused:
        current_workspaces = get_current_workspaces()
        if focused in current_workspaces:
            i3.focus_workspace(focused)
            logger.debug(f"Restored focus to workspace '{focused}'")
        else:
            logger.debug(f"Previously focused workspace '{focused}' no longer exists")

    logger.info(f"Restored {successful} workspace(s), skipped {skipped}")

    return 0
