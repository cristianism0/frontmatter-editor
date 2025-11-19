import logging
from pathlib import Path

# Select the PATH, use a '.' if you're already on it.
PATH = Path('.')

# Do you want to backup all your files on a BACKUP directory?
# YES -> True (default)
# NO -> False
BACKUP = True

# If you want to exclude a directory from being touched, move it to backup:
# Secret directories (starts with a .) will be ignored by default.
EXCLUDE_DIRS = ["BACKUP"]

def backup_dir(MD_files: list, choice: bool = BACKUP):
    """Create a BACKUP directory on the PATH.""" 
    if choice:
        backup_path = Path('BACKUP')
        backup_path.mkdir(parents = True, exist_ok = True)
        for files in MD_files:
            files.copy_into('BACKUP', preserve_metadata = True)
    else:
        print("Backup folder was not created.")


def collect_dirs_md(PATH: object = PATH):
    """Collect all subdirectories from PATH and all md files on each of it."""

    # Collects all child names for visualization
    CHILD_NAMES = [child.name for child in PATH.iterdir() if child.is_dir()]

    logging.warning("Directories accessed: %s", CHILD_NAMES)
    print("\nIf you want to remove any of it, put on EXCLUDE_DIR.")

    # Iterate over all directories and find .md files:
    md_files = list(PATH.rglob('**.md'))

    return md_files

def meta_data_reader():
    """Read all meta data from the folders."""
    return 0

