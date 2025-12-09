from pathlib import Path

# Select the PATH, use a '.' if you're already on it.
PATH = Path('.')

# Do you want to backup all your files on a BACKUP directory?
# YES -> True (default)
# NO -> False
CREATE_BACKUP = False

# If you want to change backup directory path, change the path inside Path('new/path').
BACKUP_PATH = PATH / 'BACKUP'

# If you want to exclude a directory from being touched, move it to backup:
# Secret directories (starts with a .) will be ignored by default.
# Backup is EXCLUDED by default.
EXCLUDE_DIRS = []

# DRY RUN prevents any alteration on files
# FALSE by default for secure, change to TRUE to activate the script

DRY_RUN_MODE = True
