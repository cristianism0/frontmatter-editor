#!/usr/bin/env python3

from pathlib import Path
import time 
from src.utils import sub_proceed, backup_dir, json_maker
from src.file_handle.file_manager import collect_dirs_and_files, metadata_remover, metadata_set_update

# Select the PATH, use a '.' if you're already on it.
PATH = Path('Vault')

# Do you want to backup all your files on a BACKUP directory?
# YES -> True (default)
# NO -> False
CREATE_BACKUP = False

# If you want to change backup directory path, change the path inside Path('new/path').
BACKUP_PATH = PATH / 'BACKUP'

# Path to keep logs with changes.
LOG_PATH = Path('change_logs')

# If you want to exclude a directory from being touched, move it to backup:
# Secret directories (starts with a .) will be ignored by default.
# Backup is EXCLUDED by default.
EXCLUDE_DIRS = []

# DRY RUN prevents any alteration on files
# FALSE by default for secure, change to TRUE to activate the script
DRY_RUN_MODE = False

def main():
    print("FRONTMATTER CHANGER")
    init_time = time.time()
    # Start data colleting
    try:
        dirs, files = collect_dirs_and_files(
            path = PATH,
            exclude_dirs = EXCLUDE_DIRS,
            backup_path = BACKUP_PATH
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
        if not DRY_RUN_MODE:
            if CREATE_BACKUP:
                if Path(BACKUP_PATH).exists():
                    print("BACKUP directory already exists!\n")
                    print("WARNING: if there's files with the same name, they will be overwritten.")
                else:    
                    BACKUP_PATH.mkdir()
                    print(f"A BACKUP directory was created at: {str(BACKUP_PATH)}\n")

                backup_dir(
                    MD_files= files,
                    backup_path = BACKUP_PATH,
                    ROOT_PATH =PATH)

                print(f"BACKUP done. Check before continue at: {BACKUP_PATH}")
            else:
                print("\nBackup directory was NOT created.")

        else:
            print("\nBackup directory was NOT created. DRY-RUN is TRUE.")


    except Exception as e:
        print(f"An error ocurred during BACKUP creation: {e}")
        ## Asks if want to proceed without a backup dir. not recommended.
        if not sub_proceed("Want to proceed anyway? [Y/n]:  "):
            return []
        
    # Start the script
    print("\nSTARTING THE SCRIPT\n")

    while True:
        print("Select operation:")
        print("1 - Remove frontmatter by keys")
        print("2 - Change or Update frontmatter by keys")
        print("q - Quit")

        try:
            output = str(input("Type your choice: ")).strip()
        except Exception as e:
            print(f"Oops! An error ocurred: {e}")

        ### Script Body:
        if output == '1':
            # Start remove section.
            rm_key = input("Type the key you want to remove: ")

            if not sub_proceed(f"\nWant to proceed with remove all the content with key: '{rm_key}' ? [Y/n]  "):
                return []
            else:
                remove_keys, prev_delete, post_delete, status_front_delete, actions_delete = metadata_remover(
                key=rm_key,
                files=files,
                dry_run=DRY_RUN_MODE)
               
                json_maker(
                        json_path=LOG_PATH,
                        files=files,
                        keys=remove_keys,
                        previous=prev_delete,
                        new= post_delete,
                        status=status_front_delete,
                        action=actions_delete,
                        dry_run=DRY_RUN_MODE)
               
                end_time = time.time()
                print(f"Script finished. Execution time: {(end_time - init_time):.4f} s. \n")    
               
        elif output == '2':
            # Start the changer or set section
            print("ATTENTION: CHANGE OR ADD\n")
            print("If the key already exists on the file, the content will be UPDATED\n")
            print("If the key doesn't exists on the file, the content and the key will be ADDED\n")

            up_key = input("Type the key you want to add or update: \n")
            up_content = input("Type the content you want to add or update: \n")

            if not sub_proceed(f"\nWant to proceed with remove all the content with key: '{up_key}' ? [Y/n] "):
                return []
            else:
                # CHange or ADD a content by key
                change_upt_keys, prev_change_upt, post_change_upt, status_front_change_upt, actions_change_upt = metadata_set_update(
                key= up_key,
                content= up_content,
                files=files,
                dry_run=DRY_RUN_MODE)
               
                json_maker(
                        json_path=LOG_PATH,
                        files=files,
                        keys=change_upt_keys,
                        previous=prev_change_upt,
                        new= post_change_upt,
                        status=status_front_change_upt,
                        action=actions_change_upt,
                        dry_run=DRY_RUN_MODE)
               
                end_time = time.time()
                print(f"Script finished. Execution time: {(end_time - init_time):.4f} s.\n")  


        else:
            # Close the script
            end_time = time.time()
            print(f"Closing script. Execution time: {(end_time - init_time):.4f} s.")
            break

if __name__ == '__main__':
    main()
