import logging
from pathlib import Path
from pathlib import PurePath

# Select the PATH, use a '.' if you're already on it.
PATH = Path('.')

# Do you want to backup all your files on a BACKUP directory?
# YES -> True (default)
# NO -> False
BACKUP = True

# If you want to exclude a directory from being touched, move it to backup:
# Secret directories (starts with a .) will be ignored by default.
# Backup is EXCLUDED by default.
EXCLUDE_DIRS = ["BACKUP"]

def proceed(line: str) -> bool:
    """Ask for proceed a task"""
    output = str(input(line)).lower().strip()
    if output == 'y':
        return True
    else:
        return False


def backup_dir(MD_files: list, choice: bool = BACKUP):
    """Create a BACKUP directory on the PATH."""

    if Path('BACKUP').exists():
        print('BACKUP directory already exists!')
        print("You can remove or create a new BACKUP inside BACKUP directory.")

        output = proceed("Do you want to proceed? [Y/n]:  ")
        if output == False: print("Backup folder was not created.")

        if choice:
            backup_path = Path('BACKUP')
            backup_path.mkdir(exist_ok = True)

            # It will creater a parent folder for each file for better organization.
            for files in MD_files:
                path = PurePath(files)
                parent_path = backup_path / path.parent 
                parent_path.mkdir(exist_ok= True)

                # It will copy a file in its respective parent name.
                # If the MD is on the root, it will move to backup.
                if path.parent == PurePath():
                    files.copy_into('BACKUP', preserve_metadata = True)

                else:
                    files.copy_into(parent_path, preserve_metadata = True)
                    
    else:
        print("Backup folder was not created.")



def collect_dirs_md(PATH: object = PATH, EXCLUDE_DIRS: list = EXCLUDE_DIRS):
    """Collect all subdirectories from PATH and all md files on each of it."""

    # Filter hidden directories and from EXCLUDE DIRS.
    CHILD_NAMES = [child.name for child in PATH.iterdir()
                   if not child.name.startswith('.') 
                   and child.name not in EXCLUDE_DIRS
                   and child.is_dir()]


    #This log is for another function
    print("WARNING: SubDirectories accessed: %s", CHILD_NAMES)
    print("If you want to remove any of it, put on EXCLUDE_DIR.\n")

    # Iterate over all directories and find .md files:
    md_files = list(PATH.rglob('**.md'))

    return md_files

def meta_data_reader():
    """Read all meta data from the folders."""
    return 0



### DEBUG

md = collect_dirs_md()
backup_dir(md)