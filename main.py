#!/usr/bin/env python3

from pathlib import Path, PurePath
import json

from config import PATH, CREATE_BACKUP, BACKUP_PATH, EXCLUDE_DIRS, DRY_RUN_MODE
from file_manager import backup_dir, filter_dirs, collect_dirs_and_files, metadata_remover, metadata_changer

def main():
    print("FRONTMATTER CHANGER\n\n")

    # Start data colleting
    try:
        dirs, files = collect_dirs_and_files(
            path = PATH,
            exclude_dirs = EXCLUDE_DIRS
        )

    except Exception as e:
        print(f"Cannot collect .md files: {e}")
        return []

    print(f"TOTAL FILES COLLECTED: {len(files)}")

    # Create a BACKUP folder
    try: 
        backup_dir(
            MD_files= files,
            backup_path = BACKUP_PATH,
            create_backup= CREATE_BACKUP
            )
    except Exception as e:
        print(f"An error ocurred during BACKUP creation: {e}")
    



if __name__ == '__main__':
    main()
