import json
import textwrap
from pathlib import Path

from src.utils import backup_dir, filter_dirs, json_templater, json_maker, sub_proceed


# ---------------------------------------------------------------------------
# sub_proceed
# ---------------------------------------------------------------------------
class TestSubProceed:
    def test_returns_true_on_y(self, mocker):
        mocker.patch("builtins.input", return_value="y")
        assert sub_proceed("continue? ") is True

    def test_returns_true_on_uppercase_y(self, mocker):
        mocker.patch("builtins.input", return_value="Y")
        assert sub_proceed("continue? ") is True

    def test_returns_true_on_whitespace_y(self, mocker):
        mocker.patch("builtins.input", return_value="  y  ")
        assert sub_proceed("continue? ") is True

    def test_returns_false_on_n(self, mocker):
        mocker.patch("builtins.input", return_value="n")
        assert sub_proceed("continue? ") is False

    def test_returns_false_on_empty(self, mocker):
        mocker.patch("builtins.input", return_value="")
        assert sub_proceed("continue? ") is False

    def test_returns_false_on_any_other_input(self, mocker):
        mocker.patch("builtins.input", return_value="maybe")
        assert sub_proceed("continue? ") is False


# ---------------------------------------------------------------------------
# backup_dir
# ---------------------------------------------------------------------------
class TestBackupDir:
    def test_copies_root_files(self, tmp_path):
        root1 = tmp_path / "root1.md"
        root2 = tmp_path / "root2.md"
        for p in (root1, root2):
            p.write_text("content")

        backup_path = tmp_path / "BACKUP"
        backup_dir(files=[root1, root2], backup_path=backup_path, ROOT_PATH=tmp_path)

        assert (backup_path / "root1.md").exists()
        assert (backup_path / "root2.md").exists()

    def test_preserves_subdirectory_structure(self, tmp_path):
        child = tmp_path / "visible" / "child_one"
        child.mkdir(parents=True)
        f1 = child / "file1.md"
        f1.write_text("content")

        backup_path = tmp_path / "BACKUP"
        backup_dir(files=[f1], backup_path=backup_path, ROOT_PATH=tmp_path)

        assert (backup_path / "visible/child_one/file1.md").exists()

    def test_preserves_file_content(self, tmp_path):
        f = tmp_path / "note.md"
        f.write_text("hello world")

        backup_path = tmp_path / "BACKUP"
        backup_dir(files=[f], backup_path=backup_path, ROOT_PATH=tmp_path)

        assert (backup_path / "note.md").read_text() == "hello world"

    def test_empty_file_list(self, tmp_path):
        backup_path = tmp_path / "BACKUP"
        backup_dir(files=[], backup_path=backup_path, ROOT_PATH=tmp_path)
        assert not backup_path.exists()


# ---------------------------------------------------------------------------
# filter_dirs
# ---------------------------------------------------------------------------
class TestFilterDirs:
    def test_excludes_hidden_dirs(self, tmp_path):
        hidden = tmp_path / ".hidden"
        visible = tmp_path / "visible"
        hidden.mkdir()
        visible.mkdir()

        result = filter_dirs(path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup")
        assert hidden not in result
        assert visible in result

    def test_excludes_backup_dir(self, tmp_path):
        backup = tmp_path / "backup"
        backup.mkdir()

        result = filter_dirs(path=tmp_path, exclude_dirs=[], backup_path=backup)
        assert backup not in result

    def test_excludes_custom_dirs(self, tmp_path):
        excl = tmp_path / "excluded"
        ok = tmp_path / "included"
        excl.mkdir()
        ok.mkdir()

        result = filter_dirs(path=tmp_path, exclude_dirs=["excluded"], backup_path=tmp_path / "backup")
        assert excl not in result
        assert ok in result

    def test_excludes_children_of_excluded_dirs(self, tmp_path):
        excl = tmp_path / "excluded"
        child = excl / "child"
        child.mkdir(parents=True)

        result = filter_dirs(path=tmp_path, exclude_dirs=["excluded"], backup_path=tmp_path / "backup")
        assert excl not in result
        assert child not in result

    def test_empty_directory(self, tmp_path):
        result = filter_dirs(path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup")
        assert result == []


# ---------------------------------------------------------------------------
# json_templater
# ---------------------------------------------------------------------------
class TestJsonTemplater:
    def test_single_file(self, tmp_path):
        f = tmp_path / "note.md"
        f.touch()
        result = json_templater([f])
        assert len(result) == 1
        assert result[0]["title"] == "note.md"
        assert result[0]["path"] == f.as_posix()

    def test_multiple_files(self, tmp_path):
        files = [tmp_path / f"f{i}.md" for i in range(3)]
        for f in files:
            f.touch()
        result = json_templater(files)
        assert len(result) == 3
        titles = [e["title"] for e in result]
        assert titles == ["f0.md", "f1.md", "f2.md"]

    def test_empty_list(self):
        assert json_templater([]) == []

    def test_nested_path(self, tmp_path):
        nested = tmp_path / "a" / "b"
        nested.mkdir(parents=True)
        f = nested / "deep.md"
        f.touch()
        result = json_templater([f])
        assert result[0]["path"] == f.as_posix()


# ---------------------------------------------------------------------------
# json_maker
# ---------------------------------------------------------------------------
class TestJsonMaker:
    def test_creates_log_file_dry_run(self, tmp_path, mocker):
        files = [tmp_path / "a.md"]
        log_dir = tmp_path / "logs"
        keys = {files[0].as_posix(): "title"}
        previous = {files[0].as_posix(): "Old"}
        new = {files[0].as_posix(): "removed"}
        status = {files[0].as_posix(): "has frontmatter"}
        action = {files[0].as_posix(): "remove"}

        result = json_maker(
            log_dir=log_dir, files=files, keys=keys,
            previous=previous, new=new, status=status,
            action=action, dry_run=True,
        )

        assert len(result) == 1
        assert result[0]["key"] == "title"
        assert result[0]["old_value"] == "Old"
        json_files = list(log_dir.glob("dry-run_*.json"))
        assert len(json_files) == 1

    def test_creates_log_file_real_run(self, tmp_path):
        files = [tmp_path / "a.md"]
        log_dir = tmp_path / "logs"
        keys = {files[0].as_posix(): "tag"}
        previous = {files[0].as_posix(): None}
        new = {files[0].as_posix(): "new_tag"}
        status = {files[0].as_posix(): "has frontmatter"}
        action = {files[0].as_posix(): "add"}

        json_maker(
            log_dir=log_dir, files=files, keys=keys,
            previous=previous, new=new, status=status,
            action=action, dry_run=False,
        )

        json_files = list(log_dir.glob("changes_*.json"))
        assert len(json_files) == 1

    def test_log_content_matches_input(self, tmp_path):
        f = tmp_path / "note.md"
        f.touch()
        log_dir = tmp_path / "logs"
        fkey = f.as_posix()

        json_maker(
            log_dir=log_dir, files=[f],
            keys={fkey: "title"},
            previous={fkey: "v1"},
            new={fkey: "v2"},
            status={fkey: "ok"},
            action={fkey: "change"},
            dry_run=False,
        )

        json_file = list(log_dir.glob("changes_*.json"))[0]
        data = json.loads(json_file.read_text())
        assert data[0]["title"] == "note.md"
        assert data[0]["key"] == "title"
        assert data[0]["old_value"] == "v1"
        assert data[0]["new_value"] == "v2"

    def test_creates_log_dir_if_missing(self, tmp_path):
        log_dir = tmp_path / "deep" / "nested" / "logs"
        f = tmp_path / "x.md"
        f.touch()

        json_maker(
            log_dir=log_dir, files=[f],
            keys={f.as_posix(): "k"},
            previous={f.as_posix(): None},
            new={f.as_posix(): "v"},
            status={f.as_posix(): "s"},
            action={f.as_posix(): "a"},
            dry_run=False,
        )

        assert log_dir.exists()
