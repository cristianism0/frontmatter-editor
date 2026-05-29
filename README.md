# FrontMatter Editor

CLI tool to read, add, update, or remove frontmatter keys across multiple Markdown files recursively. Built for bulk operations on Obsidian vaults and similar directory structures.

## Features

- **Remove** a frontmatter key from all files in a directory
- **Add or update** a frontmatter key across all files
- **Dry-run mode** — simulates all operations without modifying any file
- **Backup** — copies original files before any modification
- **JSON log** — records every change (or simulated change) with key,
  old value, new value, action, and frontmatter status per file

## Requirements

- Python >= 3.14 - Uses `pathlib.PosixPath.copy_into()` introduced in 3.14.
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
git clone https://github.com/cristianism0/frontmatter-editor.git
cd frontmatter-editor
uv sync
```

With pip:

```bash
pip install -r requirements.txt
```

## Usage

```bash
uv run main.py <path> [options]
```

### Options

| Flag | Description |
|---|---|
| `--dry-run` | Simulate without modifying files |
| `--backup` | Create backup before modifying |
| `--backup-path PATH` | Custom backup directory (default: `<path>/backup`) |
| `--exclude DIR ...` | Directories to skip (default: `.git`, `node_modules`, `__pycache__`) |
| `--log-path PATH` | Path for JSON log file (default: `<path>/frontmatter_log.json`) |

### Examples

```bash
# Dry-run: simulate changes, no files modified
uv run main.py /path/to/vault --dry-run

# Remove a key with backup
uv run main.py /path/to/vault --backup --dry-run
# confirm results in the log, then run without --dry-run

# Add or update a key, excluding a directory
uv run main.py /path/to/vault --exclude templates --backup
```

## JSON log

Every run produces a log file with one entry per file:

```json
[
    {
        "title": "note.md",
        "path": "vault/folder/note.md",
        "key": "tags",
        "old_value": "null",
        "new_value": "devops",
        "action": "added",
        "status_frontmatter": "present"
    }
]
```

Dry-run logs are prefixed with `dry-run_`. Real runs are prefixed with `changes_`.

## Limitations

- Tested on UNIX systems only. Windows support is untested — use `--backup`
  before running on Windows.
- Does not handle nested frontmatter keys.
  - Does not work on `+++//+++` kind.

## Running tests

```bash
uv run pytest
```