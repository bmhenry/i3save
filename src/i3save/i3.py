"""i3-msg wrapper module for communicating with i3 window manager."""

import json
import subprocess
from typing import Any

from .exceptions import I3CommandError, I3MsgNotFoundError, I3NotRunningError


def run_i3_msg(message_type: str, command: str | None = None) -> Any:
    """Execute i3-msg and return parsed JSON output.

    Args:
        message_type: The i3-msg message type (e.g., 'get_workspaces', 'get_outputs', 'command')
        command: Optional command string for 'command' message type

    Returns:
        Parsed JSON response from i3-msg (dict or list depending on message type)

    Raises:
        I3MsgNotFoundError: If i3-msg is not found in PATH
        I3NotRunningError: If i3 is not running or IPC connection fails
        I3CommandError: If i3-msg command fails or JSON parsing fails
    """
    cmd = ["i3-msg", "-t", message_type]

    if command is not None:
        cmd.append(command)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError:
        raise I3MsgNotFoundError("i3-msg not found in PATH. Is i3 installed?")

    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
        if "Could not connect to i3" in error_msg or "IPC" in error_msg:
            raise I3NotRunningError("i3 is not running or IPC connection failed")
        raise I3CommandError(f"i3-msg failed: {error_msg}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise I3CommandError(f"Failed to parse i3-msg output as JSON: {e}")


def get_workspaces() -> list[dict]:
    """Get list of all workspaces from i3.

    Returns:
        List of workspace objects, each containing keys like:
        - name: Workspace name/number
        - output: Monitor/output the workspace is on
        - focused: Whether this workspace is currently focused
        - visible: Whether workspace is visible on its output
        - urgent: Whether workspace has urgent hint
    """
    return run_i3_msg("get_workspaces")


def get_outputs() -> list[dict]:
    """Get list of all outputs/monitors from i3.

    Returns:
        List of output objects, each containing keys like:
        - name: Output name (e.g., 'HDMI-1', 'DP-2')
        - active: Whether output is active
        - rect: Dict with x, y, width, height
        - current_workspace: Name of workspace currently shown
    """
    return run_i3_msg("get_outputs")


def move_workspace_to_output(workspace_name: str, output_name: str) -> bool:
    """Move a workspace to a specified output/monitor.

    Args:
        workspace_name: Name of the workspace to move
        output_name: Name of the target output (e.g., 'HDMI-1')

    Returns:
        True if command succeeded, False otherwise
    """
    command = f'[workspace="{workspace_name}"] move workspace to output {output_name}'
    result = run_i3_msg("command", command)

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("success", False)
    return False


def focus_workspace(workspace_name: str) -> bool:
    """Switch focus to a specified workspace.

    Args:
        workspace_name: Name of the workspace to focus

    Returns:
        True if command succeeded, False otherwise
    """
    command = f'workspace "{workspace_name}"'
    result = run_i3_msg("command", command)

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("success", False)
    return False
