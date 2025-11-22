#!/usr/bin/env python3

from pathlib import Path, PurePath
import json

from config import PATH, CREATE_BACKUP, BACKUP_PATH, EXCLUDE_DIRS, DRY_RUN_MODE
from file_manager import backup_dir, collect_dirs_and_files, metadata_remover, metadata_changer
from file_manager import json_maker, sub_proceed

def main():
    print("FRONTMATTER CHANGER\n")

    # Start data colleting
    try:
        dirs, files = collect_dirs_and_files(
            path = PATH,
            exclude_dirs = EXCLUDE_DIRS
        )

        dir_name = [d.name for d in dirs]
        print("\nINFO: Directories accessed: ",dir_name)

        files_name = [name for name in files]
        print(f"FILES: {files_name}")
        print(f"FILES COUNT: {len(files)}")

    except Exception as e:
        print(f"Cannot collect .md files: {e}")
        return []

    # Create a BACKUP folder
    try: 
        if CREATE_BACKUP:
            if Path(BACKUP_PATH).exists():
                print("BACKUP directory already exists!\n")
                print("WARNING: if there's files with the same name, they will be overwritten.")
            else:    
                BACKUP_PATH.mkdir()
                print(f"A BACKUP directory was created at: {str(BACKUP_PATH)}\n")

            backup_dir(
                MD_files= files,
                backup_path = BACKUP_PATH,)

            print(f"BACKUP done. Check before continue at: {BACKUP_PATH}")
        else:
            print("\nBackup directory was NOT created.")

    except Exception as e:
        print(f"An error ocurred during BACKUP creation: {e}")
        ## Asks if want to proceed without a backup dir. not recommended.
        if not sub_proceed("Want to proceed anyway? [Y/n]:  "):
            return []
        
    # Start the script
    print("#######################")
    print("\nSTARTING THE SCRIPT\n")
    print("#######################")

    while True:
        print("Select operation:")
        print("1 - Remove frontmatter by keys")
        print("2 - Change frontmatter by keys")
        print("q - Quit")

        try:
            output = int(input("Type your choice: ")).strip()
        except Exception as e:
            print("Oops! An error ocurred: {e}")


        ### Script Body:

        match output:
            case 'q':
                break
            
            case 1:
            # REMOVE FRONT MATTER
                print("INFO: The key is the word before ':'. IT'S CASE SENSITIVE!\n")
                key = str(input("Type the key that you want to delete: "))






if __name__ == '__main__':
    main()
