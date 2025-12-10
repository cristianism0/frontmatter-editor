from pathlib import Path
from typing import List, Tuple
from ..utils import filter_dirs
from ..frontmatter_handler.parser import load_frontmatter


def collect_dirs_and_files(path: Path, exclude_dirs: list, backup_path: Path ) -> Tuple[List[Path], list]:
    """Collect all subdirectories from path and all md files on each of it."""
    
    filtered_dirs = filter_dirs(path, exclude_dirs, backup_path)

    md_files = []
    # Iterate over all directories and find .md files:
    for dirs in filtered_dirs:
        # Collect files on selected subdirectories
        files = list((path / dirs).glob("*.md"))
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

def metadata_remover(key: str, files: list, dry_run: bool) -> Tuple[dict, dict, dict, dict, dict]:
    """Remove one key of the frontmatter and its value."""
    previous_delete_content = {}
    after_delete_content = {}
    status_frontmatter = {}
    actions = {}
    keys = {}

    for file in files:
        try:
            # collect the file content
            header_lines, body_lines, has_frontmatter = load_frontmatter(file)
        except:
            print(f"{file} was not changed.")
            if not dry_run:
                file_reconstruct(file, new_header, body_lines, has_frontmatter)
            else:
                continue
            
        # Save content for log:
        file_key = file.as_posix()

        if has_frontmatter:
            status_frontmatter[file_key] = f"{file} has frontmatter"
        else:
            status_frontmatter[file_key] = f"{file} doesn't have frontmatter"

        old_value = header_lines.get(key)

        previous_delete_content[file_key] = old_value

        actions[file_key] = "remove"
        keys[file_key] = key

        # Create a new header_lines for manipulation
        new_header = header_lines.copy()
        try:
            #delete the key provided in the new header
            new_header.pop(key)        
            # For log -> Put None
            after_delete_content[file_key] = None

        except Exception as e:
            # It will capture failured.
            #print(f"A error has ocurred on file: {file}. ERROR: {e} ")
            #for log
            after_delete_content[file_key] = "!!!FAILED!!!"
            continue

        if not dry_run:
            file_reconstruct(file, new_header, body_lines, has_frontmatter)
 
    return keys, previous_delete_content, after_delete_content, status_frontmatter, actions

def metadata_set_update(key: str, content: str, files: list, dry_run: bool) -> Tuple[dict, dict, dict, dict, dict]:
    """Change the value of one key of the frontmatter."""
    previous_change_content = {}
    after_change_content = {}
    status_frontmatter = {}
    actions = {}
    keys = {}

    for file in files:
        header_lines, body_lines, has_frontmatter = load_frontmatter(file)

        # Save content for log:
        file_key = file.as_posix()

        if has_frontmatter:
            status_frontmatter[file_key] = f"{file} has frontmatter"
        else:
            status_frontmatter[file_key] = f"{file} doesn't have frontmatter"

        old_value = header_lines.get(key)      #the value with the key that i gave
        new_value = content                    #new value is the content

        previous_change_content[file_key] = old_value

        if key in header_lines:
            actions[file_key] = "change" 
        else:
            actions[file_key] = "add" 

        keys[file_key] = key


        # Create a new header_lines for manipulation 
        new_header = header_lines.copy()
        try:
            new_header[key] = content

            # for log
            after_change_content[file_key] = new_value

        except Exception as e:
            # It will capture failured.
            #print(f"Cannot change the {key} value: {e} not found in {file}")
            # for log
            after_change_content[file_key] = old_value
            continue
        if not dry_run:
            file_reconstruct(file, new_header, body_lines, has_frontmatter)
 
    return keys, previous_change_content, after_change_content, status_frontmatter, actions
