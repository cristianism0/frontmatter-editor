from pathlib import Path
from typing import Tuple
import yaml
import re

def load_frontmatter(file) -> Tuple[dict, str, bool]:
    """Parser the file and get content using Regex"""

    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"

    full_file_pattern = r"(.*)$"
    # ^---\s+ -> starts with --- and can have whitespaces
    #(.*?) -> get everything (non-greedy)
    # then close the match and get all the file content.

    raw_content = file.read_text(encoding='utf8')

    has_frontmatter = bool

    try:
        match = re.search(pattern, raw_content, re.DOTALL | re.MULTILINE)

        frontmatter = yaml.safe_load(match[1])
        # return the frontmatter in a dictionary:
        #ready to call the metadata functions already.

        file_content = match[2]
        has_frontmatter = True

        # Special case: if the frontmatter is a list only.
        if type(frontmatter) == list:
            return {}, match[0], False

        return frontmatter, file_content, has_frontmatter

    except:
        print(f"{file} does not have YAML Frontmatter!\n")
        raw_file_content = re.search(full_file_pattern, raw_content, re.DOTALL | re.MULTILINE)

        file_content = raw_file_content[0]

        empty_frontmatter = {}
        has_frontmatter = False

    return empty_frontmatter, file_content, has_frontmatter

