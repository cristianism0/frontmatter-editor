# FrontMatter Editor

This is Python script is made to: Open, read, alter or remove FrontMatter content in 
`markdown (.md)` files.

The stroger use if for alter a big bunch of `md` file fast, usually, *Obsidian Vaults*.

## How to use:
### WARNING
The script is written to be used in UNIX systems. The path style used here is *forward slashes*, even `pathlib` has a support for it, yet, **i don't tested**.
If you are using *Windows*, create a BACKUP before use the script.

### Requirements:
- Git
- *a directory*
- Python >= 3.14 
- PyYAML 25.7.0

1. Clone the repository:
```bash
git clone https://github.com/cristianism0/Frontmatter-Script.git
```

1. **EDIT MAIN FILE**: Here is the heart of the script.
```bash
cd Metadata-Changer
nano main.py          #or whatever text editor you like
```

In `main.py` you will need to change the options for your script:
- If you want a backup directory.
- Your directory path.
- **If your script will run or not.**

1. Once made the edits, move the files to your directory:
```bash
cd Metadata-Changer
mv file_manager.py your/directory/with/md/.py
mv main.py your/directory/with/md/.py
```
1. Execute it:
```bash
chmod a+rwx main.py && ./main.py
```
Or if you dont want to set a `chmod`, just use Python:
```bash
python main.py
uv run main.py #if you are using uv (and you should)
``` 