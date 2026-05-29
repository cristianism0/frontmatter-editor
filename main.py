#!/usr/bin/env python3
"""
FRONTMATTER CHANGER
Script para gerenciar frontmatter de arquivos Markdown
"""

import argparse
import time
from pathlib import Path
from src.utils import sub_proceed, backup_dir, json_maker
from src.file_handle.file_manager import collect_dirs_and_files, metadata_remover, metadata_set_update

def parse_arguments():
    """
    Configure and process command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Manage frontmatter of Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Normal mode with backup
  python main.py /path/to/folder --backup
  
  # Dry-run mode (simulate without modifying)
  python main.py /path/to/folder --dry-run
  
  # Dry-run mode with backup
  python main.py /path/to/folder --dry-run --backup
  
  # Specify directories to exclude
  python main.py /path/to/folder --exclude .git node_modules
  
  # Customize backup path
  python main.py /path/to/folder --backup --backup-path ./my_backup
        """
    )
    
    # Required argument: directory
    parser.add_argument(
        'path',
        type=str,
        help='Path to directory containing Markdown files'
    )
    
    # Optional arguments
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate modifications without altering files'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup of files before modifying'
    )
    
    parser.add_argument(
        '--backup-path',
        type=str,
        default=None,
        help='Custom path for backup directory (default: PATH/backup)'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=['.git', 'node_modules', '__pycache__'],
        help='Directories to exclude from search (default: .git node_modules __pycache__)'
    )
    
    parser.add_argument(
        '--log-path',
        type=str,
        default=None,
        help='Path to save JSON log file (default: PATH/frontmatter_log.json)'
    )
    parser.add_argument(
        '--log-path',
        type=str,
        default=None,
        help='Directory to save JSON log files (default: <path>/frontmatter_log/)'
    )
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Settings based on arguments
    PATH = Path(args.path).resolve()
    DRY_RUN_MODE = args.dry_run
    CREATE_BACKUP = args.backup
    EXCLUDE_DIRS = args.exclude
    
    # Define backup and log paths
    if args.backup_path:
        BACKUP_PATH = Path(args.backup_path).resolve()
    else:
        BACKUP_PATH = PATH / 'backup'
    
    if args.log_path:
        LOG_DIR = Path(args.log_path).resolve()
    else:
        LOG_DIR = PATH / 'frontmatter_log'
    
    # Validate PATH
    if not PATH.exists():
        print(f"ERROR: The directory '{PATH}' does not exist!")
        return
    
    if not PATH.is_dir():
        print(f"ERROR: '{PATH}' is not a directory!")
        return
    
    # Display settings
    print("="*60)
    print("FRONTMATTER CHANGER")
    print("="*60)
    print(f"Directory: {PATH}")
    print(f"Dry-Run Mode: {'YES' if DRY_RUN_MODE else 'NO'}")
    print(f"Create Backup: {'YES' if CREATE_BACKUP else 'NO'}")
    if CREATE_BACKUP:
        print(f"Backup Path: {BACKUP_PATH}")
    print(f"Excluded Directories: {', '.join(EXCLUDE_DIRS)}")
    print(f"Log Path: {LOG_PATH}")
    print("="*60)
    print()
    
    init_time = time.time()
    
    # Start data collecting
    try:
        dirs, files = collect_dirs_and_files(
            path=PATH,
            exclude_dirs=EXCLUDE_DIRS,
            backup_path=BACKUP_PATH
        )

        dir_name = [d.name for d in dirs]
        print("\nINFO: Directories accessed:", dir_name)

        files_name = [name for name in files]
        print(f"FILES: {files_name}")
        print(f"FILES COUNT: {len(files)}")

    except Exception as e:
        print(f"Cannot collect .md files: {e}")
        return

    # Create a BACKUP folder
    try: 
        if not DRY_RUN_MODE:
            if CREATE_BACKUP:
                if Path(BACKUP_PATH).exists():
                    print("BACKUP directory already exists!\n")
                    print("WARNING: if there's files with the same name, they will be overwritten.")
                else:    
                    BACKUP_PATH.mkdir(parents=True)
                    print(f"A BACKUP directory was created at: {str(BACKUP_PATH)}\n")

                backup_dir(
                    files=files,
                    backup_path=BACKUP_PATH,
                    ROOT_PATH=PATH)

                print(f"BACKUP done. Check before continue at: {BACKUP_PATH}")
            else:
                print("\nBackup directory was NOT created.")

        else:
            print("\nBackup directory was NOT created. DRY-RUN is TRUE.")

    except Exception as e:
        print(f"An error occurred during BACKUP creation: {e}")
        ## Asks if want to proceed without a backup dir. not recommended.
        if not sub_proceed("Want to proceed anyway? [Y/n]:  "):
            return
        
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
            print(f"Oops! An error occurred: {e}")
            continue

        ### Script Body:
        if output == '1':
            # Start remove section.
            rm_key = input("Type the key you want to remove: ")

            if not sub_proceed(f"\nWant to proceed with remove all the content with key: '{rm_key}' ? [Y/n]  "):
                continue
            else:
                remove_keys, prev_delete, post_delete, status_front_delete, actions_delete = metadata_remover(
                    key=rm_key,
                    files=files,
                    dry_run=DRY_RUN_MODE)
               
                json_maker(
                    log_dir=LOG_DIR,
                    files=files,
                    keys=remove_keys,
                    previous=prev_delete,
                    new=post_delete,
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

            if not sub_proceed(f"\nWant to proceed with add/update key: '{up_key}' ? [Y/n] "):
                continue
            else:
                # Change or ADD a content by key
                change_upt_keys, prev_change_upt, post_change_upt, status_front_change_upt, actions_change_upt = metadata_set_update(
                    key=up_key,
                    content=up_content,
                    files=files,
                    dry_run=DRY_RUN_MODE)
               
                json_maker(
                    json_path=LOG_PATH,
                    files=files,
                    keys=change_upt_keys,
                    previous=prev_change_upt,
                    new=post_change_upt,
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
