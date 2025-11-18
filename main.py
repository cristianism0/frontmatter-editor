import os
from pathlib import Path

PATH = Path('.')                                           # Select the PATH, use a '.' if you're already on it.
SUB_dir = [sub for sub in PATH.iterdir() if sub.is_dir()]  # Returns all subdirectories in PATH

def sub_dir_join(SUB_dir_list = SUB_dir):
    for sub_directory in SUB_dir_list:




