import yaml
from pathlib import Path

file1 = Path('teste_yaml.md')
malformed = Path('malformed.md')


def safe_load_frontmatter(file):
    """Safe load the frontmatter using PyYAML"""

    with file.open() as f:
        try:
            front = yaml.safe_load(f)
            print(yaml.dump(front))

        # Mal formed YAML -> return the entire file for write again    
        except:
            return file    

    return 0

print(f"{safe_load_frontmatter(malformed)} malformed")
safe_load_frontmatter(file1)


