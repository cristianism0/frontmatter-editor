import pytest
from src.file_handle.file_manager import  collect_dirs_and_files, file_reconstruct, frontmatter_collector
from src.file_handle.file_manager import  metadata_remover, metadata_add, metadata_changer


# PASSED
def test_collect_dirs_and_files(tmp_path):
    d = tmp_path / "docs"
    excluded = tmp_path / "excluded"

    d.mkdir()
    excluded.mkdir()

    ex_file = excluded / 'ex_file.md'
    file1 = d / 'file1.md'
    file2 = d / 'file2.md'


    ex_file.write_text("---\ntest: excluded\n---\n")
    file1.write_text("---\ntest: num 1\n---\n")
    file2.write_text("---\ntest: num 2\n---\n")

    dirs, files = collect_dirs_and_files(path = tmp_path, exclude_dirs = [excluded], backup_path = tmp_path / "backup")

    assert d in dirs
    assert file1 in files
    assert file1 in files
    assert excluded not in files


