"""Save functionality for i3save - captures workspace-to-output mappings."""

import json
from pathlib import Path

from . import i3
from .exceptions import ConfigFileError
from .logging import Logger


def build_workspace_mapping() -> dict:
    """Build a mapping of workspaces to their current outputs.

    Queries i3 for the current workspace state and builds a JSON-serializable
    structure containing the focused workspace, visible workspaces per output,
    and all workspace-to-output mappings.

    Returns:
        Dictionary with structure:
        {
            "focused": "<name of focused workspace>",
            "visible_workspaces": [
                {"name": "<workspace name>", "output": "<output name>"},
                ...
            ],
            "workspaces": [
                {"name": "<workspace name>", "output": "<output name>"},
                ...
            ]
        }
    """
    workspaces = i3.get_workspaces()

    focused_workspace = None
    workspace_list = []
    visible_workspaces = []

    for ws in workspaces:
        workspace_list.append({
            "name": ws["name"],
            "output": ws["output"]
        })
        if ws.get("focused", False):
            focused_workspace = ws["name"]
        if ws.get("visible", False):
            visible_workspaces.append({
                "name": ws["name"],
                "output": ws["output"]
            })

    return {
        "focused": focused_workspace,
        "visible_workspaces": visible_workspaces,
        "workspaces": workspace_list
    }


def save_to_file(mapping: dict, filepath: str) -> None:
    """Write workspace mapping to a JSON file.

    Creates parent directories if they don't exist.

    Args:
        mapping: The workspace mapping dictionary to save
        filepath: Path to the output file

    Raises:
        ConfigFileError: If file cannot be written
    """
    path = Path(filepath)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(mapping, f, indent=2)
            f.write("\n")
    except OSError as e:
        raise ConfigFileError(f"Failed to write file '{filepath}': {e}")


def save(filepath: str, quiet: bool = False, verbose: bool = False) -> int:
    """Save current workspace layout to a file.

    Main entry point for the save command. Queries i3 for current workspace
    positions and saves them to the specified file.

    Args:
        filepath: Path to save the workspace mapping
        quiet: If True, suppress normal output (only show errors)
        verbose: If True, show detailed output

    Returns:
        Exit code: 0 for success, non-zero for failure

    Raises:
        I3SaveError: If i3 communication or file operations fail
    """
    logger = Logger.from_flags(quiet=quiet, verbose=verbose)

    mapping = build_workspace_mapping()

    logger.debug(f"Found {len(mapping['workspaces'])} workspace(s)")
    for ws in mapping["workspaces"]:
        logger.debug(f"  Workspace '{ws['name']}' on output '{ws['output']}'")
    if mapping.get("visible_workspaces"):
        logger.debug(f"Visible workspaces: {len(mapping['visible_workspaces'])}")
        for ws in mapping["visible_workspaces"]:
            logger.debug(f"  '{ws['name']}' visible on output '{ws['output']}'")
    if mapping["focused"]:
        logger.debug(f"Focused workspace: {mapping['focused']}")

    save_to_file(mapping, filepath)

    logger.info(f"Saved {len(mapping['workspaces'])} workspace(s) to {filepath}")

    return 0
