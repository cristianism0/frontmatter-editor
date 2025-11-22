from pathlib import Path, PurePath
import json
from config import BACKUP_PATH
from typing import List, Tuple
from datetime import datetime

from config import PATH, EXCLUDE_DIRS, DRY_RUN_MODE


def sub_proceed(line: str) -> bool:
    """Ask for proceed a task"""
    output = str(input(line)).lower().strip()
    if output == 'y':
        return True
    else:
        return False

def backup_dir(MD_files: list, backup_path: Path) -> None:
    """Create a BACKUP directory on the path."""
    # It will create a parent directory for each file for better organization.
    for files in MD_files:
        path = PurePath(files)
        parent_path = backup_path / path.parent 
        parent_path.mkdir(exist_ok= True, parents = True)
        # It will copy a file in its respective parent name.
        # If the MD is on the root, it will move to backup.
        if path.parent == PurePath():
            files.copy_into(backup_path, preserve_metadata = True)
        else:
            files.copy_into(parent_path, preserve_metadata = True)
    
    
    return None

def filter_dirs(path: Path, exclude_dirs: list, backup_path: Path = BACKUP_PATH) -> List[Path]:
    """Filter the directories: Taking out hidden and EXCLUDED"""

    # Create path for each item on exclude_dirs
    excluded_paths = [Path(dirs) for dirs in exclude_dirs]

    fun_match = lambda d: any(d.is_relative_to(expath) for expath in excluded_paths)

    filtered_dirs = [
        f for f in path.glob('**/*')          # Recursive search for dirs
        if f.is_dir()
        and not f.is_relative_to(backup_path)
        and not f.full_match('.*')
        and not f.full_match('.*/**')         # Recursive search for files inside hidden dirs
        and not fun_match(f)
    ]

    return filtered_dirs

def collect_dirs_and_files(path: Path, exclude_dirs: list ) -> Tuple[List[Path], list]:
    """Collect all subdirectories from path and all md files on each of it."""
    
    filtered_dirs = filter_dirs(path, exclude_dirs)

    md_files = []
    # Iterate over all directories and find .md files:
    for dirs in filtered_dirs:
        # Collect files on selected subdirectories
        files = list(Path(path / dirs).glob("*.md"))
        # Put all files collected here
        md_files.extend(files)


    return filtered_dirs, md_files

def file_reconstruct(file, header, body, frontmatter: bool) -> None:
    """Reconstruct the file: New header + Content"""

    with file.open(mode = 'w') as f:

        if frontmatter:
            # Open frontmatter
            f.write('---\n')
            for key, values in header.items():
                f.write(f"{key}: {values}\n")
            # Close frontmatter
            f.write('---\n')

        f.writelines(body)

def frontmatter_collector(file) -> Tuple[any, dict, dict, bool]:
    """Collect frontmatter from a .md file"""

    header_lines = {}
    body_lines = []

    # flow controllers
    inside_frontmatter = False
    has_frontmatter = False

    with file.open() as f:
        for line in f:
            # Remove all blankspaces
            stripped_line = line.strip()
            # Verify if is in frontmatter
            if stripped_line == '---':
                # if there is frontmatter, it will turn on.
                if not inside_frontmatter:
                    inside_frontmatter = True
                    has_frontmatter = True
                    continue
                else:
                # if already turned on: it will turn off.
                    inside_frontmatter = False
                    continue
                
            if inside_frontmatter:
                key, content = stripped_line.split(':', 1)
                header_lines[key.strip()] = content.strip()
            else:
                body_lines.append(line)
    
    return file, header_lines, body_lines, has_frontmatter

def metadata_remover(key: str, files: list, dry_run: bool) -> Tuple[dict, dict]:
    """Remove one key of the frontmatter and its value."""
    changed_files = len(files)

    previous_delete_content = {}
    after_delete_content = {}

    for file in files:
        file, header_lines, body_lines, has_frontmatter = frontmatter_collector(file)

        # Save content for log:
        file_key = file.as_posix()
        old_value = header_lines.get(key, "")


        previous_delete_content[key] = header_lines[key]

        # Create a new header_lines for manipulation
        new_header = header_lines

        try:
            new_header.pop(key)
            after_delete_content[file_key] = old_value

            print(f"{changed_files} was changed. {key} was removed from the frontmatter.\n")

        except KeyError as e:
            # It will capture failed ones.
            after_delete_content[key] = ""

            print(f"A error has ocurred: {e} not found in {file}")
            changed_files = changed_files - 1

    # DRY RUN WILL DEFINE TO REWRITE OR NOT THE FILES
    if dry_run:
        return previous_delete_content, after_delete_content
    else:
        file_reconstruct(file, new_header, body_lines, has_frontmatter)
        return previous_delete_content
    
def metadata_changer(key: str, content: str, files: list, dry_run: bool) -> Tuple[dict, dict]:
    """Change the value of one key of the frontmatter."""

    changed_files = len(files)

    previous_change_content = {}
    after_change_content = {}

    for file in files:
        file, header_lines, body_lines, has_frontmatter = frontmatter_collector(file)

        # Save content for log:
        file_key = file.as_posix()
        old_value = header_lines.get(key, "")
        new_value = header_lines[key]

        previous_change_content[file_key] = old_value 

        # Create a new header_lines for manipulation 
        new_header = header_lines

        try:
            new_header[key] = content
            after_change_content[file_key] = new_value
            print(f"{changed_files} was changed. {key} value was changed to {content}.\n")

        except KeyError as e:
            # It will capture failed ones.
            after_change_content[file_key] = new_value
            print(f"Cannot change the {key} value: {e} not found in {file}")
            changed_files = changed_files - 1

    if dry_run:
        return previous_change_content, after_change_content
    else:
        file_reconstruct(file, new_header, body_lines, has_frontmatter)
        return previous_change_content, after_change_content  

def json_templater(files: list) -> list:
    """Aplly template for files in json output"""
    json_complete = []

    for file in files:
        json_template = {
            "title": file.name,
            "path": file.as_posix(),
            }
        
        json_complete.append(json_template)
    
    return json_complete

def json_maker(files: list, previous: dict, new: dict, dry_run: bool) -> dict:
    """Create a JSON file with all alterations"""

    json_list = json_templater(files)

    print("==========DEBUB SECTION==========")
    print(previous)
    print("==========DEBUB SECTION==========")

    for entry, file in zip(json_list, files):

        file_key = file.as_posix()

        old_value = previous.get(file_key, "")
        new_value = new.get(file_key, "")

        entry["old"] = f"{old_value}"
        entry["new"] = f"{new_value}"
    
    if dry_run:
        json_file_name = f'dry-run_{datetime.now()}.json'
    
    else:
        json_file_name = f'changes_{datetime.now()}.json'

    json_path = Path('change_logs') / json_file_name
    json_path.parent.mkdir(parents = True, exist_ok = True)

    #JSON dumps uses ensure_ascii = True by default, which encode special char: ~, ç ...
    #This makes JSON flexible to system that can only read ASCII
    #If you want to enable do ensure_ascii = False

    with open(json_path, 'w', encoding='utf8') as json_file:
        # ensure_ascii=False 
        json.dump(json_list, json_file, indent = 4, ensure_ascii=False)

    print(f"A JSON file created at: {json_path}")

    return json_list


#################### DEBUG ###########################
files = [Path('teste1.md'), Path('teste2.md')]
old, new = metadata_changer('alterar', 'ALTEROURS', files, DRY_RUN_MODE)

for i, j in old.items():
    print(i,j)

#json_maker(files, old, new, DRY_RUN_MODE)
