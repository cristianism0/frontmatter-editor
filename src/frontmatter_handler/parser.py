import yaml
from pathlib import Path
import re



def safe_load_frontmatter(file):
    """Safe load the frontmatter using PyYAML"""

    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"

    # ^---\s+ -> starts with --- and can have whitespaces
    #(.*?) -> get everything (non-greedy)
    # then close the match and get all the file content.

    raw_content = file.read_text(encoding='utf8')

    match = re.search(pattern, raw_content, re.DOTALL | re.MULTILINE)

    with file.open() as stream:
        try:
            front = yaml.safe_load_all(stream)
            print(yaml.dump_all(front))   
        # Malformed YAML -> return the entire file for write again    
        
        except Exception as e:
            print(f'deu erro: {e}')
            return file

    return 0


