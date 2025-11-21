from pathlib import Path, PurePath
import json
from config import BACKUP_PATH

def sub_proceed(line: str) -> bool:
    """Ask for proceed a task"""
    output = str(input(line)).lower().strip()
    if output == 'y':
        return True
    else:
        return False

def backup_dir(MD_files: list, backup_path: Path, create_backup: bool):
    """Create a BACKUP directory on the path."""
    if create_backup:
        # Create the BACKUP directory
        if Path(backup_path).exists():
            print("BACKUP directory already exists!")
            print("All the .md files collected will be saved there!")
            print("WARNING: if there's files with the same name, they will be overwritten.")

        else:    
            backup_path.mkdir()
            print(f"A BACKUP directory was created at: {str(backup_dir)}")

        # It will create a parent directory for each file for better organization.
        for files in MD_files:
            path = PurePath(files)
            parent_path = backup_path / path.parent 
            parent_path.mkdir(exist_ok= True)

            # It will copy a file in its respective parent name.
            # If the MD is on the root, it will move to backup.
            if path.parent == PurePath():
                files.copy_into(backup_path, preserve_metadata = True)

            else:
                files.copy_into(parent_path, preserve_metadata = True)
                    
    else:
        print("Backup directory was not created.")

def sub_filter_dirs(path: Path, exclude_dirs: list, backup_path: Path = BACKUP_PATH):
    """Filter the directories: Taking out hidden and EXCLUDED"""

    # Create path for each item on exclude_dirs
    excluded_paths = [path(dirs) for dirs in exclude_dirs]

    # Lambda function for iterate (is_relative_to)
    relative_exclude = lambda d: any(d.is_relative_to(expath) for expath in excluded_paths)
    filtered_dirs = [
        f for f in path.glob('**/*')
        if f.is_dir()
        and not f.is_relative_to(backup_path)
        and not f.full_match('.*')
        and not f.full_match('.*/**')
        and not relative_exclude(f)
    ]

    return filtered_dirs

def collect_dirs_and_files(path: Path, exclude_dirs: list ):
    """Collect all subdirectories from path and all md files on each of it."""
    
    filtered_dirs = sub_filter_dirs(path, exclude_dirs)

    print("\nWARNING: Directories accessed: ", filtered_dirs)
    print("If you want to remove any of it, put on EXCLUDE_DIR.\n")

    root_files = list(path.glob("**.md"))
    md_files = []

    # Collect files on the root path
    md_files.extend(root_files)

    # Iterate over all directories and find .md files:
    for dirs in filtered_dirs:
        # Collect files on selected subdirectories
        files = list(Path(path / dirs).rglob("**.md"))

        # Put all files collected here
        md_files.extend(files)

    return filtered_dirs, md_files

def sub_json(dry_run: bool):
    return 0

def sub_reconstruct(file, header, body):
    """Reconstruct the file: New header + Content"""
    with file.open(mode = 'w') as f:
        for header_lines in header:
            f.write(header_lines)

        for body_lines in body:
            f.write(body_lines)

    return file

def metadata_remover(files: list):
    """Read all meta data from the folders."""
    names = map(str(), files)
    print(names)
    for file in names:
        header_lines = []
        body_lines = []
        with file.open() as f:
            for line in f:
                if line.startswith('---'):
                    header_lines.append(('---' + '\n'))
                    # Collect the header
                    while line.startswith('---') == False:
                        header_lines.append(line + '\n')

                    # Close frontmatter
                    header_lines.append(('---' + '\n'))

                else:
                    # If there is no front matter, or if already collected, get the content
                    body_lines.append(line + '\n')

        print(reconstruct(file, header_lines, body_lines))
        print("=================")
        file.read_text()
        print("=================")

    return 0

def metadata_changer(files: list):
    """Read all meta data from the folders."""
    # Iterate over FILES, so we will need md files because has full path
    for file in files:
        with file.open() as f:
            for line in f:
                if line.startswith('---'):
                    print()


    return 0
