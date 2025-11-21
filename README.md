# FrontMatter Editor

This is Python script is made to: Open, read, alter or remove FrontMatter content in 
`markdown (.md)` files.

The stroger use if for alter a big bunch of `md` file fast, usually, *Obsidian Vaults*.

## How to use:
### WARNING
The script is written to be used in UNIX systems. The path style used here is *forward slashes*, even `pathlib` has a support for it, yet, **i did not tested**.
If you are using *Windows*, create a BACKUP before use the script.

### Requirements:
- Git
- *a directory*

1. Clone the repository:
```bash
git clone https://github.com/cristianism0/Metadata-Changer.git
```

2. **EDIT CONFIG FILE**: Here is the heart of the script.
```bash
cd Metadata-Changer
nano config.py          #or whatever text editor you like
```
In `config.py` you will need to change the options for your script:
- If you want a backup directory.
- Your directory path.
- **If your script will run or not.**

3. Once made the edits, move the files to your directory:
```bash
cd Metadata-Changer
mv config.py your/directory/with/md/.py
mv file_manager.py your/directory/with/md/.py
mv main.py your/directory/with/md/.py
```

4. Execute it:
```bash
./main.py
```