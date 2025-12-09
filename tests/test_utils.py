from src.utils import backup_dir, filter_dirs

def test_backup_dir(tmp_path):
    """
    tmp/root_file1.md
    tmp/root_file2.md
    tmp/visible/child_one/file1.md
    tmp/visible/child_two/file2.md
    """
    visible = tmp_path / "visible"
    child_one = visible / "child_one"
    child_two = visible / "child_two"

    child_one.mkdir(parents=True)
    child_two.mkdir(parents=True)

    root1 = tmp_path / "root1.md"
    root2 = tmp_path / "root2.md"
    f1 = child_one / "file1.md"
    f2 = child_two / "file2.md"


    for p in [root1, root2, f1, f2]:
        p.touch()

    files = [root1, root2, f1, f2]
    backup_path = tmp_path / "BACKUP"

    backup_dir(files = files, backup_path = backup_path, ROOT_PATH = tmp_path)

    assert (backup_path / "root1.md").exists()
    assert (backup_path / "root2.md").exists()
    assert (backup_path / "visible/child_one/file1.md").exists()
    assert (backup_path / "visible/child_two/file2.md").exists()

# PASSED
def test_filter_dirs(tmp_path):
    """
    tmp/visible/child
    tmp/visible/excluded
    tmp/visible/excluded/not_excluded_child 
    tmp/root_excluded   
    tmp/.hidden
    tmp/excluded
    tmp/backup
    tmp/backup/ignored
    """

    visible = tmp_path / "visible"
    visible_child = visible / "child"
    visible_excluded = visible / "excluded"
    root_excluded = tmp_path / "excluded"
    not_excluded_child = visible / "excluded" / "not_excluded_child"
    hidden = tmp_path / ".hidden"
    backup = tmp_path / "backup"
    ignored = backup / "ignored"

    dirs = [
        visible, visible_child,
        root_excluded, visible_excluded, not_excluded_child,
        hidden, 
        backup, ignored
    ]
    for dir in dirs:
        dir.mkdir(parents=True, exist_ok=True)

    # Once created temp_path. Call the function
    result = filter_dirs(
        path=tmp_path,
        exclude_dirs=[root_excluded,visible_excluded],
        backup_path=backup  
    )

    # Assert
    assert visible in result #-> get visible child but not visible/excluded/* and visible/excluded
    assert visible_child in result

    # filtered
    assert visible_excluded not in result
    assert root_excluded not in result
    assert not_excluded_child not in result
    assert hidden not in result
    assert backup not in result
    assert ignored not in result
