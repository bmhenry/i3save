# i3save

_Disclaimer: This repository is basically entirely AI generated_

A command-line utility for i3 window manager users to save and restore workspace-to-monitor mappings.

`i3save` solves the problem of workspaces not persisting their monitor locations when switching between monitor configurations (e.g., docking/undocking a laptop).

## Requirements

- Python 3.8+
- i3 window manager
- `i3-msg` CLI tool (included with i3)

## Installation

From the project directory:

```bash
# Standard installation
pip install .

# Development installation (editable)
pip install -e .
```

## Usage

### Save workspace layout

Save the current workspace-to-monitor mapping to a file:

```bash
i3save save <file>
```

Example:
```bash
# Save before undocking
i3save save ~/.config/i3/workspaces-docked.json
```

### Restore workspace layout

Restore workspaces to their saved monitor locations:

```bash
i3save restore <file>
```

Example:
```bash
# Restore after docking
i3save restore ~/.config/i3/workspaces-docked.json
```

**Restore behavior:**
- If a workspace no longer exists, it is skipped
- If a saved monitor no longer exists, the workspace is moved to the largest available monitor
- The previously focused workspace is restored after all moves complete

### Verbosity flags

Both commands support verbosity control:

| Flag | Description |
|------|-------------|
| `-q`, `--quiet` | Suppress normal output, only show errors |
| `-v`, `--verbose` | Show detailed output for each operation |

Examples:
```bash
# Quiet mode - no output unless errors occur
i3save save -q ~/.config/i3/workspaces.json

# Verbose mode - show each workspace being processed
i3save restore -v ~/.config/i3/workspaces.json
```

### Other options

```bash
# Show version
i3save --version

# Show help
i3save --help
i3save save --help
i3save restore --help
```

## JSON file format

The saved workspace mapping uses the following JSON structure:

```json
{
  "focused": "1",
  "workspaces": [
    {"name": "1", "output": "DP-2"},
    {"name": "2", "output": "DP-2"},
    {"name": "3", "output": "HDMI-1"},
    {"name": "music", "output": "eDP-1"}
  ]
}
```

| Field | Description |
|-------|-------------|
| `focused` | Name of the workspace that was focused when saved |
| `workspaces` | List of workspace-to-output mappings |
| `workspaces[].name` | Workspace name (can be numeric or string) |
| `workspaces[].output` | Output/monitor name where the workspace resides |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (file not found, invalid JSON, etc.) |
| 2 | i3 communication error (i3 not running, i3-msg not found) |

## Example workflow

```bash
# Create workspace layout files for different configurations
i3save save ~/.config/i3/workspaces-docked.json
i3save save ~/.config/i3/workspaces-undocked.json

# Restore when switching configurations
# (can be triggered by udev rules, scripts, etc.)
i3save restore ~/.config/i3/workspaces-docked.json
```
