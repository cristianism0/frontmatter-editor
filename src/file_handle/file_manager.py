from pathlib import Path
from typing import List, Tuple
import src.utils as utils


def collect_dirs_and_files(path: Path, exclude_dirs: list, backup_path: Path ) -> Tuple[List[Path], list]:
    """Collect all subdirectories from path and all md files on each of it."""
    
    filtered_dirs = utils.filter_dirs(path, exclude_dirs, backup_path)

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

def frontmatter_collector(file) -> Tuple[dict, dict, bool]:
    """Collect frontmatter from a .md file"""

    header_lines = {}
    body_lines = []

    # flow controllers
    inside_frontmatter = False
    has_frontmatter = False

    with file.open() as f:
        lines = f.readlines()
        #Look if there is frontmatter
        if lines[0].strip().startswith('---'):
            has_frontmatter = True
            inside_frontmatter = True

        for l in lines[1:]:
            print(f"has_frontmatter value {has_frontmatter}")
            print(f"inside_frontmatter value {inside_frontmatter}\n")
            if has_frontmatter and inside_frontmatter:
                if not l.strip().startswith('---'):
                    try:
                        key, content = l.split(':', 1)
                        header_lines[key] = content
                    except:
                        # TODO -> FIX IT
                        # Thinked of: create a new module with parsing containing
                        # this fuction with separated parts to not become so overload
                        # it will because a i have to track lists and multiline comments
                        # broken yaml 
                        # TODO 
                        # The logic i thinked is: 
                        # put a position value to track line pos and compare if starts a multiline or list
                        # track the list if the stripped line endswith(':') AND if the pos(lis+1) contain
                        # line.startwith('-'), if not. i will armazena with: key '\n'.
                        # identify if there is already a key, ex: if there is 2 tags, raise a error and skip 
                        # the file as it was.

                        # if there is any error, copy the entire lines in body and send again.
                        # for file reconstruct, its good to know if there's a error or not
                        # if there is a error, it will take the same parte as NOT has frontmatter and will copy
                        #the entire file

                        continue
                else:
                    #close frontmatter
                    inside_frontmatter = False
            else:
                body_lines.append(l)

    return header_lines, body_lines, has_frontmatter

def metadata_remover(key: str, files: list, dry_run: bool) -> Tuple[dict, dict]:
    """Remove one key of the frontmatter and its value."""
    changed_files = len(files)

    previous_delete_content = {}
    after_delete_content = {}

    for file in files:
        header_lines, body_lines, has_frontmatter = frontmatter_collector(file)

        # Save content for log:
        file_key = file.as_posix()
        old_value = header_lines.get(key)

        previous_delete_content[file_key] = old_value

        # Create a new header_lines for manipulation
        new_header = header_lines.copy()

        try:
            #delete the key provided in the new header
            new_header.pop(key)
            print(f"{changed_files} was changed. {key} with was removed from the frontmatter.\n")
        
            # For log -> Maintain the old value because if was deleted
            after_delete_content[file_key] = old_value

        except Exception as e:
            # It will capture failured.
            print(f"A error has ocurred on file: {file}. ERROR: {e} ")
            changed_files = changed_files - 1

            #for log
            after_delete_content[file_key] = "!!!FAILED!!!"
            continue
        if not dry_run:
            file_reconstruct(file, new_header, body_lines, has_frontmatter)
 
    return previous_delete_content, after_delete_content

def metadata_changer(key: str, content: str, files: list, dry_run: bool) -> Tuple[dict, dict]:
    """Change the value of one key of the frontmatter."""

    changed_files = len(files)

    previous_change_content = {}
    after_change_content = {}

    for file in files:
        header_lines, body_lines, has_frontmatter = frontmatter_collector(file)

        # Save content for log:
        file_key = file.as_posix()
        old_value = header_lines.get(key)      #the value with the key that i gave
        new_value = content                    #new value is the content

        previous_change_content[file_key] = old_value 

        # Create a new header_lines for manipulation 
        new_header = header_lines.copy()

        try:
            new_header[key] = content

            # for log
            after_change_content[file_key] = new_value
            print(f"{changed_files} was changed. {key} value was changed to {content}.\n")

        except Exception as e:
            # It will capture failured.
            print(f"Cannot change the {key} value: {e} not found in {file}")
            changed_files = changed_files - 1

            # for log
            after_change_content[file_key] = old_value
            continue
        if not dry_run:
            file_reconstruct(file, new_header, body_lines, has_frontmatter)
 
    return previous_change_content, after_change_content

def metadata_add(key: str, content: str, files: list, dry_run: bool) -> Tuple[dict, dict]:
    """Add a value on the frontmatter of each file."""

    changed_files = len(files)

    previous_add_content = {}
    after_add_content = {}

    for file in files:
        header_lines, body_lines, has_frontmatter = frontmatter_collector(file)

        # Save content for log:
        file_key = file.as_posix()
        old_value = header_lines.get(key, None)  #-> Returns None
        new_value = content

        previous_add_content[file_key] = old_value 

        # Create a new header_lines for manipulation 
        new_header = header_lines.copy()

        try:
            # add the new value on the new header
            new_header[key] = new_value
            print(f"{changed_files} was changed. {key} value {content} was added to the frontmatter.\n")

            #for log
            after_add_content[file_key] = new_value

        except KeyError as e:
            # It will capture failured.
            print(f"Cannot change the {key} value: {e} not found in {file}")
            changed_files = changed_files - 1

            # for log
            after_add_content[file_key] = content
            continue
        if not dry_run:
            file_reconstruct(file, new_header, body_lines, has_frontmatter)
 
    return previous_add_content, after_add_content

