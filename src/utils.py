from pathlib import Path
from typing import List
from datetime import datetime
import json


def sub_proceed(line: str) -> bool:
    """Ask for proceed a task"""
    output = str(input(line)).lower().strip()
    if output == 'y':
        return True
    else:
        return False

def backup_dir(files: list, backup_path: Path, ROOT_PATH: Path) -> None:
    """Create a BACKUP directory on the path."""
    # It will create a parent directory for each file for better organization.
    for files in files:
        file_path = Path(files)
        relative = file_path.relative_to(ROOT_PATH)

        parent_path = backup_path / relative.parent 
        parent_path.mkdir(exist_ok= True, parents = True)
        # It will copy a file in its respective parent name.
        # If the MD is on the root, it will move to backup.
        file_path.copy_into(parent_path, preserve_metadata=True)

        # if path.parent == Path():
        #     files.copy_into(backup_path, preserve_metadata = True)
        # else:
        #     files.copy_into(parent_path, preserve_metadata = True)
    
    return None

def filter_dirs(path: Path, exclude_dirs: list, backup_path: Path) -> List[Path]:
    """Filter the directories: Taking out hidden and EXCLUDED"""

    # Create path for each item on exclude_dirs
    excluded_paths = [path / dirs for dirs in exclude_dirs]

    # Function that chech if each path is relative to another -> avoid childrens of excluded dirs.
    fun_match = lambda d: any(d.is_relative_to(expath) for expath in excluded_paths)

    filtered_dirs = [
        f for f in path.glob('**/*')          # Recursive search for dirs
        if f.is_dir()
        and not f.is_relative_to(backup_path)
        and not f.name.startswith('.')
        and not fun_match(f)
    ]

    return filtered_dirs

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

    for entry, file in zip(json_list, files):

        file_key = file.as_posix()

        old_value = previous.get(file_key)
        new_value = new.get(file_key)

        entry["old_value"] = f"{old_value}"
        entry["new_value"] = f"{new_value}"
    
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
