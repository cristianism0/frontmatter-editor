from pathlib import Path
from pathlib import PurePath

# Select the PATH, use a '.' if you're already on it.
PATH = Path('.')

# Do you want to backup all your files on a BACKUP directory?
# YES -> True (default)
# NO -> False
BACKUP = False

# If you want to change backup directory path, change the path inside Path('new/path').
BACKUP_PATH = Path('.') / 'BACKUP'

# If you want to exclude a directory from being touched, move it to backup:
# Secret directories (starts with a .) will be ignored by default.
# Backup is EXCLUDED by default.
EXCLUDE_DIRS = []

def proceed(line: str) -> bool:
    """Ask for proceed a task"""
    output = str(input(line)).lower().strip()
    if output == 'y':
        return True
    else:
        return False

def backup_dir(MD_files: list, BACKUP_PATH: Path = BACKUP_PATH, choice: bool = BACKUP):
    """Create a BACKUP directory on the PATH."""
    if choice:
        # Create the BACKUP directory
        if Path(BACKUP_PATH).exists():
            print("BACKUP directory already exists!")
            print("All the .md files collect will be saved there!")
            print("WARNING: if there's files with the same name, they will be overwritten.")

        else:    
            BACKUP_PATH.mkdir()

        # It will create a parent directory for each file for better organization.
        for files in MD_files:
            path = PurePath(files)
            parent_path = BACKUP_PATH / path.parent 
            parent_path.mkdir(exist_ok= True)

            # It will copy a file in its respective parent name.
            # If the MD is on the root, it will move to backup.
            if path.parent == PurePath():
                files.copy_into(BACKUP_PATH, preserve_metadata = True)

            else:
                files.copy_into(parent_path, preserve_metadata = True)
                    
    else:
        print("Backup directory was not created.")

def filter_dirs(PATH: Path = PATH, BACKUP_PATH: Path = BACKUP_PATH, EXCLUDE_DIRS: list = EXCLUDE_DIRS):
    """Filter the directories: Taking out hidden and EXCLUDED"""

    # Create PATH for each item on EXCLUDE_DIRS
    EXCLUDED_PATHS = [Path(dirs) for dirs in EXCLUDE_DIRS]

    # Lambda function for iterate (is_relative_to)
    relative_exclude = lambda d: any(d.is_relative_to(expath) for expath in EXCLUDED_PATHS)

    filtered_dirs = [
        f for f in PATH.glob('**/*')
        if f.is_dir()
        and not f.is_relative_to(BACKUP_PATH)
        and not f.full_match('.*')
        and not f.full_match('.*/**')
        and not relative_exclude(f)
    ]

    return filtered_dirs

def collect_dirs_and_files(PATH: object = PATH, EXCLUDE_DIRS: list = EXCLUDE_DIRS):
    """Collect all subdirectories from PATH and all md files on each of it."""
    
    filtered_dirs = filter_dirs(EXCLUDE_DIRS)

    print("\nWARNING: Directories accessed: ", filtered_dirs)
    print("If you want to remove any of it, put on EXCLUDE_DIR.\n")

    root_files = list(PATH.glob("**.md"))
    md_files = []

    # Collect files on the root path
    md_files.extend(root_files)

    # Iterate over all directories and find .md files:
    for dirs in filtered_dirs:
        # Collect files on selected subdirectories
        files = list(Path(PATH / dirs).rglob("**.md"))

        # Put all files collected here
        md_files.extend(files)

    return filtered_dirs, md_files

def reconstruct(file, header, body):
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

######################### DEBUG #################################

filter_dirs()
#dirs, files = collect_dirs_and_files()
#metadata_remover(dirs)